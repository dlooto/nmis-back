# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from django.db import models, transaction

from utils import times
from base.models import BaseModel
from nmis.devices.models import OrderedDevice

from .managers import ProjectPlanManager, ProjectFlowManager
from .consts import *


logs = logging.getLogger(__name__)


class ProjectPlan(BaseModel):
    """
    采购申请(一次申请即开始一个项目)
    """
    title = models.CharField('项目名称', max_length=30)
    purpose = models.CharField('申请原因', max_length=100, null=True, default='')
    creator = models.ForeignKey(
        'hospitals.Staff', related_name='created_projects', verbose_name='项目申请人/提出者',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    related_dept = models.ForeignKey(
        'hospitals.Department', verbose_name='申请科室',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    performer = models.ForeignKey(  # 项目新建后为空
        'hospitals.Staff', related_name='performed_projects', verbose_name='项目负责人/执行人',
        null=True, blank=True, on_delete=models.SET_NULL
    )

    attached_flow = models.ForeignKey(
        "projects.ProjectFlow", verbose_name="项目使用的流程",
        null=True, blank=True, on_delete=models.SET_NULL
    )
    current_stone = models.ForeignKey(  # 项目当前的里程碑结点
        'projects.MileStone', verbose_name='项目里程碑结点',
        null=True, blank=True, on_delete=models.SET_NULL
    )

    # 项目里程碑状态变更记录轨迹, 项目每次变更里程碑状态时添加一条记录数据
    milestones = models.ManyToManyField(
        'projects.Milestone', verbose_name=u'里程碑轨迹',
        through='projects.ProjectMilestoneRecord', through_fields=('project', 'milestone'),
        related_name="projects", related_query_name="project", blank=True
    )

    status = models.CharField('项目状态', max_length=2, choices=PROJECT_STATUS_CHOICES, default=PRO_STATUS_PENDING)
    startup_time = models.DateTimeField(u'项目启动时间', null=True, blank=True)  # 项目分配负责人的时刻即为启动时间
    expired_time = models.DateTimeField(u'项目截止时间', null=True, blank=True)

    objects = ProjectPlanManager()

    class Meta:
        verbose_name = 'A 项目申请'
        verbose_name_plural = 'A 项目申请'
        db_table = 'projects_project_plan'

    VALID_ATTRS = [
        'title', 'purpose',
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    def get_ordered_devices(self):
        """
        返回项目中包含的所有设备列表
        """
        return OrderedDevice.objects.filter(project=self)

    def is_unstarted(self):
        """ 项目是否未启动 """
        return self.status == PRO_STATUS_PENDING

    def is_undispatched(self):
        """
        是否待分配负责人状态
        :return: True or False
        """
        return self.performer is None

    def update(self, data):
        """
        仅更新项目本身的属性信息, 不修改项目内含的设备明细
        :param data:
        :return:
        """
        try:
            with transaction.atomic():
                super(self.__class__, self).update(data)
                self.clear_cache()
                return self
        except Exception as e:
            logs.exception(e)
            return None

    def create_device(self, **device_data):
        return OrderedDevice.objects.create(project=self, **device_data)

    def dispatch(self, performer, **data):
        """
        分派项目给某个员工作为责任人. 项目分配责任人后即进入启动状态
        :param performer:  要分派的责任人, staff object
        :param data: dict parameters, 一般情况下需要有flow, expired_time等参数
        :return: True or False
        """
        try:
            with transaction.atomic():
                self.performer = performer
                self.attached_flow = data.pop("flow")
                self.expired_time = data.pop("expired_time")
                self.status = PRO_STATUS_STARTED
                self.startup_time = times.now()

                self.current_stone = self.attached_flow.get_first_milestone()
                self.add_milestone_record(self.current_stone)

                self.save()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def add_milestone_record(self, milestone):
        """
        项目每变更一次里程碑状态, 则添加一条里程碑状态记录
        :param milestone: Milestone object
        :return: True or False
        """
        try:
            ProjectMilestoneRecord.objects.create(project=self, milestone=milestone)
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def get_recorded_milestones(self):
        """
        返回已进行到的里程碑节点列表
        :return:
        """
        return self.milestones.all()

    def get_milestone_changed_records(self):
        """
        返回项目里程碑变更记录列表
        :return: ProjectMilestoneRecord object
        """
        return ProjectMilestoneRecord.objects.filter(project=self)

    def contains_recorded_milestone(self, milestone):
        """
        判断里程碑状态是否存在项目状态列表记录中
        :param milestone:
        :return:
        """
        if milestone in self.get_recorded_milestones():
            return True
        return False

    def change_milestone(self, new_milestone):
        """
        变更项目里程碑状态
        :param new_milestone: 新的里程碑状态对象
        :return: True or False
        """
        if self.is_unstarted():
            return False, "项目尚未启动"

        if not self.attached_flow.contains(new_milestone):
            return False, "里程碑项不属于当前所用流程, 请检查数据是否异常"

        if new_milestone == self.current_stone:
            return False, "已处于该状态"

        if new_milestone in self.get_recorded_milestones():
            return False, "里程碑已存在项目状态记录中"

        try:
            with transaction.atomic():
                self.add_milestone_record(new_milestone)
                self.current_stone = new_milestone
                self.save()
            return True, "变更成功"
        except Exception as e:
            logs.exception(e)
            return False, "数据异常"


class ProjectFlow(BaseModel):
    """
    项目流程
    """
    organ = models.ForeignKey('hospitals.Hospital', verbose_name='所属医院', on_delete=models.CASCADE)
    title = models.CharField('流程名称', max_length=30, default='默认')
    type = models.CharField('流程类型', max_length=3, null=True, blank=True, default='')
    pre_defined = models.BooleanField('是否预定义', default=False) # 机构初始创建时, 为机构默认生成预定义的流程

    objects = ProjectFlowManager()

    class Meta:
        verbose_name = 'B 项目流程'
        verbose_name_plural = 'B 项目流程'
        db_table = 'projects_project_flow'

    def __str__(self):
        return "%s %s" % (self.id, self.title)

    def get_milestones(self):
        """ 流程内含的里程碑列表 """
        return self.milestone_set.all()

    def get_first_milestone(self):
        """ 返回流程中的第1个里程碑项 """
        return self.get_milestones().order_by('index')[:1][0]

    def contains(self, milestone):
        """
        流程中是否包含指定milestone
        :param milestone:
        :return:
        """
        return milestone in self.get_milestones()

    def get_last_milestone(self):
        """ 返回流程中的最后一个里程碑项 """
        pass


class Milestone(BaseModel):
    """
    项目里程碑结点
    """
    flow = models.ForeignKey('projects.ProjectFlow', verbose_name='归属流程', on_delete=models.CASCADE)
    title = models.CharField('里程碑标题', max_length=10, )

    # 用于决定里程碑项在流程中的顺序. index值小的排在前面
    index = models.SmallIntegerField('索引顺序', default=1)
    desc = models.CharField('描述', max_length=20, default='')

    class Meta:
        verbose_name = '里程碑项'
        verbose_name_plural = '里程碑项'
        db_table = 'projects_milestone'
        ordering = ['index']

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    def next(self, ):
        """
        返回当前里程碑项在流程中的下一个里程碑项
        :return: milestone
        """
        it = iter(self.flow.get_milestones().order_by('index')) # 迭代器
        while True:
            try:
                m = next(it)
                if m == self:
                    return next(it)
            except StopIteration:
                return None

    def previous(self):
        """ 上一个里程碑项 """
        pass


class ProjectMilestoneRecord(BaseModel):
    """
    项目里程碑变更记录. m/m关系: 一个项目的生命周期内, 有多条变更记录存在. 一个里程碑项可被多个项目
     使用.
    """
    project = models.ForeignKey('projects.ProjectPlan', verbose_name='项目', on_delete=models.CASCADE)
    milestone = models.ForeignKey(
        'projects.Milestone', verbose_name='里程碑节点', on_delete=models.SET_NULL,
        null=True, blank=True
    )
    # doc_list = models.CharField()  # 文档列表

    class Meta:
        verbose_name = '项目里程碑记录'
        verbose_name_plural = '项目里程碑记录'
        db_table = 'projects_project_milestone_record'

    def __str__(self):
        return self.project_id, self.milestone_id


# class Contract(BaseModel):
#     """
#     采购合同
#     """
#
#     class Meta:
#         verbose_name = u'采购合同'
#         verbose_name_plural = u'采购合同'
#         db_table = 'projects_contract'
#
#
# class Supplier(BaseModel):
#     """
#     供应商
#     """
#
#     class Meta:
#         verbose_name = u'供应商'
#         verbose_name_plural = u'供应商'
#         db_table = 'projects_supplier'
