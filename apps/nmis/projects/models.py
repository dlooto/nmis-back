# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from django.db import models

from base.models import BaseModel
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
    current_stone = models.ForeignKey( # 项目当前的里程碑结点
        'projects.MileStone', verbose_name='项目里程碑结点',
        null=True, blank=True, on_delete=models.SET_NULL
    )
    status = models.CharField('项目状态', max_length=2, choices=PROJECT_STATUS_CHOICES, default=PRO_STATUS_PENDING)

    objects = ProjectPlanManager()

    class Meta:
        verbose_name = 'A 项目申请'
        verbose_name_plural = 'A 项目申请'
        db_table = 'projects_project_plan'

    def __str__(self):
        return self.title


class ProjectFlow(BaseModel):
    """
    项目流程
    """
    hospital = models.ForeignKey('hospitals.Hospital', verbose_name='所属医院',
                                on_delete=models.CASCADE)
    title = models.CharField('流程名称', max_length=30, default='默认')
    type = models.CharField('流程类型', max_length=3, null=True, blank=True,default='')
    pre_defined = models.BooleanField('是否预定义', default=False) # 机构初始创建时, 为机构默认生成预定义的流程

    objects = ProjectFlowManager()

    class Meta:
        verbose_name = 'B 项目流程'
        verbose_name_plural = 'B 项目流程'
        db_table = 'projects_project_flow'

    def __str__(self):
        return self.title


class Milestone(BaseModel):
    """
    项目里程碑结点
    """
    flow = models.ForeignKey('projects.ProjectFlow', verbose_name='归属流程', on_delete=models.CASCADE)
    title = models.CharField('里程碑标题', max_length=10, )
    index = models.SmallIntegerField('索引顺序', default=1) # 用于决定里程碑项在流程中的顺序
    desc = models.CharField('描述', max_length=20, default='')

    class Meta:
        verbose_name = '里程碑项'
        verbose_name_plural = '里程碑项'
        db_table = 'projects_milestone'

    def __str__(self):
        return self.title

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
