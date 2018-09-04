# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from collections import OrderedDict
from django.db import models, transaction

from nmis.projects.managers import ProjectDocumentManager, ProjectMilestoneRecordManager
from utils import times
from base.models import BaseModel
from nmis.devices.models import OrderedDevice, SoftwareDevice

from .managers import ProjectPlanManager, ProjectFlowManager, \
    ProjectOperationRecordManager
from .consts import *


logs = logging.getLogger(__name__)


class ProjectPlan(BaseModel):
    """
    采购申请(一次申请即开始一个项目)
    """
    title = models.CharField('项目名称', max_length=30)
    handing_type = models.CharField('办理方式', max_length=2,
                                    choices=PROJECT_HANDING_TYPE_CHOICES,
                                    default=PRO_HANDING_TYPE_SELF)
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

    assistant = models.ForeignKey(
        'hospitals.staff', related_name='assisted_projects', verbose_name='协助办理人',
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
    project_cate = models.CharField('项目类型', max_length=2, choices=PROJECT_CATE_CHOICES, default=PRO_CATE_HARDWARE)

    project_introduce = models.CharField('项目介绍/项目描述', max_length=200, null=True, blank=True)
    pre_amount = models.FloatField('项目预估总价', null=True, blank=True)
    procurement_method = models.CharField(
        '采购方式', max_length=20, choices=PORJECT_PROCUREMENT_METHOD_CHOICES,
        null=True, blank=True
    )

    objects = ProjectPlanManager()

    class Meta:
        verbose_name = 'A 项目申请'
        verbose_name_plural = 'A 项目申请'
        db_table = 'projects_project_plan'

    VALID_ATTRS = [
        'title', 'purpose', 'handing_type', 'project_introduce', 'pre_amount'
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.title)

    def get_hardware_devices(self):
        """
        返回项目中包含的所有硬件设备列表
        """
        return OrderedDevice.objects.filter(project=self)

    def get_software_devices(self):
        """
        返回信息化项目包含的所有硬件设备列表
        :return:
        """
        return SoftwareDevice.objects.filter(project=self)

    def is_unstarted(self):
        """ 项目是否未启动 """
        return self.status == PRO_STATUS_PENDING

    def is_finished(self):
        """项目是否已经完成"""
        return self.status == PRO_STATUS_DONE

    def is_paused(self):
        """ 项目是否被挂起 """
        return self.status == PRO_STATUS_PAUSE

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

    def deleted(self):
        """
        删除申请项目，被分配的项目不能删除
        """
        try:
            self.clear_cache()
            self.delete()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def create_device(self, **device_data):
        return OrderedDevice.objects.create(project=self, **device_data)

    def change_status(self, status, **data):
        """
        改变项目状态
        """
        try:
            with transaction.atomic():
                self.status = status
                self.save()
                ProjectOperationRecord.objects.add_operation_records(**data)
                self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def cancel_pause(self):
        """
        取消挂起的项目
        """
        try:
            self.status = PRO_STATUS_STARTED
            self.save()
            self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def dispatch(self, performer):
        """
        分派项目给某个员工作为责任人.项目状态改变，项目直接进入第一个里程碑
        :param performer:  要分派的责任人, staff object
        """
        try:
            with transaction.atomic():
                self.performer = performer

                self.attached_flow = self.get_default_flow()

                self.status = PRO_STATUS_STARTED
                self.startup_time = times.now()

                self.current_stone = self.attached_flow.get_first_main_milestone()
                self.add_milestone_record(self.current_stone)

                self.save()
                self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def dispatched_assistant(self, assistant):
        """
        项目负责人分配项目协助人
        :param: assistant: 项目协助人
        """
        try:
            self.assistant = assistant
            self.save()
            self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def get_default_flow(self):
        """
        返回默认流程
        """
        return ProjectFlow.objects.filter(default_flow=True).first()

    def redispatch(self, performer):
        """
        分派项目给某个员工作为责任人.项目状态改变，项目直接进入第一个里程碑
        :param performer:  要分派的责任人, staff object
        """
        try:
            with transaction.atomic():
                self.performer = performer
                self.save()
                self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def startup(self, flow, expired_time, **data):
        """
        责任人启动项目，选择协助办理人和项目截至日期
        :param flow: 协助办理人
        :param expired_time: 项目截至时间
        :param data: dict parameters, 一般情况下需要有assistant等参数
        :return: True or False
        """
        try:
            with transaction.atomic():
                if data and data['assistant']:
                    self.assistant = data['assistant']
                self.attached_flow = flow
                self.expired_time = expired_time
                self.startup_time = times.now()
                self.status = PRO_STATUS_STARTED
                self.current_stone = self.attached_flow.get_first_main_milestone()
                self.add_milestone_record(self.current_stone)
                self.save()
                self.cache()
            return True
        except Exception as e:
            logs.exception(e)
            return False

    def add_milestone_record(self, milestone):
        """
        项目每变更一次里程碑状态, 则添加一条里程碑状态记录
        默认里程碑节点深度为2，大于2须进行重构
        :param milestone: Milestone object
        :return: True or False
        """
        try:
            record = ProjectMilestoneRecord.objects.create(project=self, milestone=milestone)
            if not milestone.has_children():
                return True, [record, ]
            first_child = milestone.flow.get_first_child(milestone=milestone)
            child_record = ProjectMilestoneRecord.objects.create(project=self, milestone=first_child)
            return True, [record, child_record]

        except Exception as e:
            logs.exception(e)
            return False, "添加失败"

    def add_or_update_milestone_record(self, milestone):
        """
        项目每变更一次里程碑状态, 则没有添加一条里程碑状态记录，有就更新
        默认里程碑节点深度为2，大于2须进行重构
        :param milestone: Milestone object
        :return: True or False
        """
        if not milestone:
            return False, "milestone参数不能为空"
        try:
            record = ProjectMilestoneRecord.objects.update_or_create(project=self, milestone=milestone)
            if not milestone.has_children():
                return True, [record, ]
            first_child = milestone.flow.get_first_child(milestone=milestone)
            child_record = ProjectMilestoneRecord.objects.update_or_create(project=self, milestone=first_child)
            return True, [record, child_record]

        except Exception as e:
            logs.exception(e)
            return False, "添加失败"

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

    def finish_project_milestone(self, current_milestone):
        """
        变更项目里程碑状态
        默认里程碑节点深度为2，大于2须进行重构
        :param current_milestone: 新的里程碑状态对象
        :return: True or False
        """
        if self.is_unstarted():
            return False, "项目尚未启动无法操作。"

        if self.is_finished():
            return False, "项目已完成，无法操作。"

        if self.is_paused():
            return False, "项目已挂起，无法操作。"

        if not self.attached_flow.contains(current_milestone):
            return False, "里程碑项不属于当前所用流程, 请检查数据是否异常。"

        record_query = ProjectMilestoneRecord.objects.filter(project=self, milestone=current_milestone)
        if not record_query:
            return False, '未匹配到项目里程碑变更记录，请检查数据是否异。'
        record = record_query.first()
        if record.finished:
            return False, '该里程碑状态已完结，无法操作。'

        try:
            with transaction.atomic():
                record.finished = True
                record.save()
                if current_milestone.is_flow_last_descendant():
                    ancestor_milestone_records = ProjectMilestoneRecord.objects.filter(
                        project=self, milestone__in=current_milestone.ancestors()
                    )
                    if ancestor_milestone_records:
                        for milestone_record in ancestor_milestone_records:
                            milestone_record.finished = True
                            milestone_record.save()
                    self.status = PRO_STATUS_DONE
                    self.save()
                    self.cache()
                else:
                    next_stone = current_milestone.next()
                    logs.info('---------------')

                    logs.info(next_stone)
                    #             return True, [record, child_record]
                    success, pro_milestone_records = self.add_or_update_milestone_record(next_stone)
                    # for record, result in pro_milestone_records:
                    logs.info(pro_milestone_records)
                    pro_milestone_record, result = pro_milestone_records[-1]
                    self.current_stone = pro_milestone_record.milestone
                    self.save()
                    self.cache()
                return True, "变更成功"
        except Exception as e:
            logs.exception(e)
            return False, "数据异常"

    def change_milestone(self, new_milestone, done_sign, finished=False):
        """
        变更项目里程碑状态
        :param new_milestone: 新的里程碑状态对象
        :return: True or False
        """
        if self.is_unstarted():
            return False, "项目尚未启动"

        if not self.attached_flow.contains(new_milestone):
            return False, "里程碑项不属于当前所用流程, 请检查数据是否异常"

        if not new_milestone == self.current_stone and \
                new_milestone in self.get_recorded_milestones():
            return False, "里程碑已存在项目状态记录中"

        if new_milestone == self.current_stone:
            if done_sign == FLOW_UNDONE:
                return False, "数据异常"
            if done_sign == FLOW_DONE and self.attached_flow.get_last_main_milestone() == new_milestone:
                self.status = PRO_STATUS_DONE
                self.save()
                self.cache()
                return True, "变更成功"
            return False, "数据异常"
        try:
            with transaction.atomic():
                self.add_milestone_record(new_milestone)
                self.current_stone = new_milestone
                self.save()
                self.cache()
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
    default_flow = models.BooleanField('是否为默认流程', default=False)

    objects = ProjectFlowManager()

    class Meta:
        verbose_name = 'B 项目流程'
        verbose_name_plural = 'B 项目流程'
        db_table = 'projects_project_flow'

    VALID_ATTRS = [
        'title',
    ]

    def __str__(self):
        return "%s %s" % (self.id, self.title)

    def get_milestones(self):
        """ 流程内含的所有里程碑列表 """
        return self.milestones.all()

    def get_main_milestones(self):
        """ 流程内含的祖里程碑列表 """
        return self.milestones.filter(parent=None).order_by('index')

    def get_first_main_milestone(self):
        """ 返回流程中的第1个主里程碑项 """
        return self.get_main_milestones().order_by('index')[:1][0]

    def get_first_child(self, milestone):
        """
        获取流程某父里程碑项的第一个子里程碑
        :param milestone:
        :return:
        """
        milestones = self.get_milestones()
        if milestone not in milestones:
            return None
        if not milestone.children():
            return None
        return milestone.children().first()

    def contains(self, milestone):
        """
        流程中是否包含指定milestone
        :param milestone:
        :return:
        """
        return milestone in self.get_milestones()

    def get_last_main_milestone(self):
        """ 返回流程中的最后一个主里程碑项 """
        return self.get_main_milestones().order_by('-index')[:1][0]

    def get_last_descendant(self):
        """返回流程中最后一个子孙里程碑"""
        last_main_milestone = self.get_last_main_milestone()
        if not last_main_milestone:
            return None
        return self.get_milestone_last_descendant(last_main_milestone)

    def get_milestone_last_descendant(self, milestone):
        """返回流程中某一父里程碑最后一个子孙里程碑"""
        if not milestone:
            return None
        if not milestone.has_children():
            return milestone
        return self.get_milestone_last_descendant(milestone.last_child())

    def get_last_child(self, milestone):
        """
         获取流程某父里程碑项的最后一个子里程碑
        :return:
        """
        milestones = self.get_milestones()
        if milestone not in milestones:
            return None
        if not milestone.children():
            return None
        return milestone.children().last()

    def is_used(self):
        query_set = ProjectPlan.objects.filter(attached_flow=self)
        if not query_set:
            return False
        return True


class Milestone(BaseModel):
    """
    项目里程碑结点
    """
    flow = models.ForeignKey(
        'projects.ProjectFlow', verbose_name='归属流程', null=False,
        related_name='milestones', on_delete=models.CASCADE
    )
    title = models.CharField('里程碑标题', max_length=10, )

    # 用于决定里程碑项在流程中的顺序. index值小的排在前面
    index = models.SmallIntegerField('索引顺序', default=1)
    desc = models.CharField('描述', max_length=20, default='')

    parent = models.ForeignKey('self', verbose_name='父里程碑', null=True, on_delete=models.CASCADE)
    # 祖里程碑到当前里程碑最短路径, 由各里程碑项id的字符串组成，每个id,之间用‘-’进行分隔
    parent_path = models.CharField('父里程碑路径', max_length=1024, default='', null=False, blank=False)

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

        if not self.parent:
            if not self.has_children():
                it = iter(self.flow.get_main_milestones().order_by('index'))  # 迭代器
                while True:
                    try:
                        m = next(it)
                        if m == self:
                            return next(it)
                    except StopIteration:
                        return None
            else:
                return self.first_child()

        if self.is_last_child():
            parent = self.parent
            it = iter(parent.flow.get_main_milestones().order_by('index'))
            while True:
                try:
                    m = next(it)
                    if m == parent:
                        return next(it)
                except StopIteration:
                    return None

            return self.parent.next()

        it = iter(self.parent.children())
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

    def children(self):
        """
        返回当前里程碑项在流程中的所有直接子里程碑项
        :return: milestone list
        """
        milestones = self.flow.get_milestones().filter(parent=self).order_by('index')
        if milestones is None:
            return []
        return milestones

    def first_child(self):
        """返回当前里程碑项中index值最大的子里程碑项"""
        milestones = self.flow.get_milestones().filter(parent=self).order_by('index')
        if milestones is None:
            return []
        return milestones.first()

    def last_child(self):
        """返回当前里程碑项中index值最大的子里程碑项"""
        milestones = self.flow.get_milestones().filter(parent=self).order_by('-index')
        if milestones is None:
            return []
        return milestones.first()

    def descendants(self):
        """
        返回当前里程碑项在流程中的所有子孙里程碑项
        :return: milestones list
        """
        milestones = self.flow.get_milestones()
        descendants = []
        for milestone in milestones:
            if self.id in milestone.parent_path.split('-'):
                descendants.append(milestone)
        return descendants

    def ancestors(self):
        """
        返回当前里程碑项在流程中的所有祖先里程碑项
        :return: milestones list
        """
        if not self.parent_path:
            return []

        descendant_ids = self.parent_path.split('-')
        milestones = self.flow.get_milestones()
        ancestors = []
        for milestone in milestones:
            if milestone.id in descendant_ids:
                ancestors.append(milestone)
        return ancestors

    def has_children(self):
        """
        当前里程碑项在流程中是否有子里程碑项
        :return: True/False
        """
        if not self.children():
            return False
        return True

    def is_flow_last_descendant(self):
        """
        当前里程碑项是否为流程中最后一个子孙里程碑项
        :return:
        """
        last_descendant = self.flow.get_last_descendant()
        if not last_descendant == self:
            return False
        return True

    def is_last_descendant(self):
        """
        当前里程碑项是否为某里程碑最后一个子孙里程碑项
        :return:
        """
        if not self.parent:
            return False
        last_descendant = self.flow.get_milestone_last_descendant(milestone=self)
        if not last_descendant == self:
            return False
        return True

    def is_last_child(self):
        """
        当前里程碑项是否为父里程碑下最后一个子里程碑项
        :return:
        """
        if not self.parent:
            return False

        if not self == self.parent.last_child():
            return False
        return True

    def is_last_main_milstone(self):
        """
        当前里程碑项是否为流程中最后一个主里程碑项
        :return:
        """
        last = self.flow.get_main_milestones().last()
        if not self == last:
            return False
        return True


class ProjectMilestoneRecord(BaseModel):
    """
    项目里程碑变更记录. m/m关系: 一个项目的生命周期内, 有多条变更记录存在. 一个里程碑项可被多个项目
     使用.
    """
    project = models.ForeignKey(
        'projects.ProjectPlan', verbose_name='项目', on_delete=models.CASCADE,
        related_name='project_milestone_records',
    )
    milestone = models.ForeignKey(
        'projects.Milestone', verbose_name='里程碑节点', on_delete=models.SET_NULL,
        related_name='project_milestone_records', null=True, blank=True
    )

    # 记录在每个里程碑下操作文件上传后形成的文档集合
    doc_list = models.CharField('文档列表', max_length=100, null=True, blank=True)

    # 记录各里程碑下的一个总结性说明概述
    summary = models.TextField('总结说明', max_length=200, null=True, blank=True)

    finished = models.BooleanField("节点任务是否完结", default=False, )

    objects = ProjectMilestoneRecordManager()

    class Meta:
        verbose_name = '项目里程碑记录'
        verbose_name_plural = '项目里程碑记录'
        db_table = 'projects_project_milestone_record'

    def __str__(self):
        return '%s %s' % (self.project_id, self.milestone_id)

    def get_doc_list(self):
        """
        获取当前节点下的所有文档资料
        :return:
        """
        pass

    def get_supplier_selection_plans(self):
        """
        获取当前节点下供应商选择方案列表
        """
        pass

    def get_purchase_contract(self):
        """
        获取当前节点下采购合同信息
        :return:
        """
        pass

    def get_receipt(self):
        """
        获取当前节点下的收货确认单
        :return:
        """
        pass


class ProjectDocument(BaseModel):
    """
    项目文档数据模型
    """
    name = models.CharField('文档名称', max_length=80, null=False, blank=False)
    category = models.CharField(
        '文档类别', max_length=30, choices=PROJECT_DOCUMENT_CATE_CHOICES,
        null=False, blank=False
    )
    path = models.CharField('存放路径', max_length=255, null=False, blank=False)

    objects = ProjectDocumentManager()

    class Meta:
        verbose_name = '文档资料'
        verbose_name_plural = verbose_name
        db_table = 'projects_project_document'

    VALID_ATTRS = [
        'name', 'category', 'path'
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)


class Supplier(BaseModel):
    """
    供应商
    """
    name = models.CharField('供应商名称', max_length=100, null=False, blank=False)
    contact = models.CharField('联系人', max_length=50, null=True, blank=True)
    contact_tel = models.CharField('联系电话', max_length=12, null=True, blank=True)

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        db_table = 'projects_supplier'

    VALID_ATTRS = [
        'name', 'contact', 'contact_tel',
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)


class SupplierSelectionPlan(BaseModel):
    """
    供应商选择方案
    """
    project_milestone_record = models.ForeignKey(
        'projects.ProjectMilestoneRecord', verbose_name='所属项目里程碑子节点', on_delete=models.CASCADE,
        null=False, blank=False
    )
    supplier = models.ForeignKey(
        Supplier, verbose_name='供应商', on_delete=models.CASCADE,
        null=False, blank=False
    )
    total_amount = models.FloatField('方案总价', default=0.00, null=False, blank=False)
    remark = models.CharField('备注', max_length=255, null=True, blank=True)
    # ProjectDocument对象ID集，每个id之间用'|'字符进行分割(目前包含方案资料和其他资料)
    doc_list = models.CharField('方案文档列表', max_length=32, null=True, blank=True)
    selected = models.BooleanField('是否为最终选定方案', default=False, null=False, blank=True)

    class Meta:
        verbose_name = '供应商选择方案'
        verbose_name_plural = verbose_name
        db_table = 'projects_supplier_selection_plan'

    VALID_ATTRS = [
        'total_amount', 'remark', 'doc_list', 'selected'
    ]

    def __str__(self):
        return '%s' % (self.id,)

    def is_selected(self):
        return self.selected


class PurchaseContract(BaseModel):
    """
    采购合同
    """
    project_milestone_record = models.ForeignKey(
        'projects.ProjectMilestoneRecord', verbose_name='所属项目里程碑子节点', on_delete=models.CASCADE,
        null=False, blank=False
    )
    contract_no = models.CharField('合同编号', max_length=30, null=False, blank=False)
    title = models.CharField('合同名称', max_length=100, null=False, blank=False)
    signed_date = models.DateField('签订时间', null=False, blank=False)
    buyer = models.CharField('买方/甲方单位', max_length=128, null=False, blank=False)
    buyer_contact = models.CharField('买方/甲方联系人', max_length=50, null=False, blank=False)
    buyer_tel = models.CharField('买方/甲方联系电话', max_length=11, null=False, blank=False)
    seller = models.CharField('卖方/乙方单位', max_length=128, null=False, blank=False)
    seller_contact = models.CharField('卖方/乙方联系人', max_length=50, null=False, blank=False)
    seller_tel = models.CharField('卖方/乙方联系电话', max_length=11, null=False, blank=False)
    total_amount = models.FloatField('合同总价', default=0.00, null=False, blank=False)
    delivery_date = models.DateField('交货时间', null=False, blank=False)
    # 合同文档附件-ProjectDocument对象ID集，每个id之间用'|'字符进行分割
    doc_list = models.CharField('合同文档列表', max_length=20, null=True, blank=True)

    class Meta:
        verbose_name = u'采购合同'
        verbose_name_plural = verbose_name
        db_table = 'projects_purchase_contract'

    VALID_ATTRS = [
        'contract_no', 'title', 'signed_date',
        'buyer', 'buyer_contact', 'buyer_tel',
        'seller', 'seller_contact', 'seller_tel',
        'total_amount', 'delivery_date', 'doc_list',
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.contract_no)


class Receipt(BaseModel):
    """
    收货确认单
    """
    project_milestone_record = models.ForeignKey(
        'projects.ProjectMilestoneRecord', verbose_name='所属项目里程碑子节点', on_delete=models.CASCADE,
        null=False, blank=False
    )
    served_date = models.DateField('到货时间', null=False, blank=False)
    delivery_man = models.CharField('送货人', max_length=50, null=False, blank=False)
    contact_phone = models.CharField('联系电话', max_length=11, null=True, blank=True)
    # 送货单附件-ProjectDocument对象ID集，每个id之间用'|'字符进行分割
    doc_list = models.CharField('送货单附件', max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = u'收货确认单'
        verbose_name_plural = verbose_name
        db_table = 'projects_receipt'

    VALID_ATTRS = [
        'served_date', 'delivery_man', 'contact_phone', 'doc_list'
    ]

    def __str__(self):
        return '%d' % (self.id, )


class ProjectOperationRecord(BaseModel):
    """
    项目操作日志
    """
    project = models.IntegerField('项目')
    # 操作驳回和挂起时填写的原因
    reason = models.TextField('原因')
    operation = models.CharField('操作方式', max_length=10, choices=PROJECT_OPERATION_CHOICES)

    objects = ProjectOperationRecordManager()

    class Meta:
        verbose_name = u'项目操作日志'
        verbose_name_plural = verbose_name
        db_table = 'projects_operation_record'
