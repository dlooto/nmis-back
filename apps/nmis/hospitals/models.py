# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
组织/机构相关数据模型
"""

import logging

from django.db import models

from base.models import BaseModel
from nmis.hospitals.managers import GroupManager

from organs.models import BaseOrgan, BaseStaff, BaseDepartment, BaseGroup
from .managers import StaffManager, HospitalManager

from .consts import *

logs = logging.getLogger(__name__)


class Hospital(BaseOrgan):
    """
    医疗机构数据模型
    """

    parent = models.ForeignKey('self', verbose_name=u'上级医疗单位', on_delete=models.SET_NULL, null=True, blank=True)
    grade = models.CharField('分类等级', choices=HOSP_GRADE_CHOICES, max_length=10, null=True, blank=True, default='')

    objects = HospitalManager()

    class Meta:
        verbose_name = u'A 医疗机构'
        verbose_name_plural = u'A 医疗机构'
        db_table = 'hosp_hospital'


class Department(BaseDepartment):
    """
    医疗机构下设科室数据模型
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医疗机构', on_delete=models.CASCADE) # 重写父类
    attri = models.CharField('科室/部门属性', choices=DPT_ATTRI_CHOICES, max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = u'A 科室/部门'
        verbose_name_plural = u'A 科室/部门'
        db_table = 'hosp_department'

    def __str__(self):
        return u'%s' % self.name


class Staff(BaseStaff):
    """
    医疗机构一般员工(非医生)
    """

    # 一个员工仅属于一个企业
    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', on_delete=models.CASCADE, null=True, blank=True)
    dept = models.ForeignKey(Department, verbose_name=u'所属科室/部门', on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey('hospitals.Group', verbose_name=u'权限组', null=True, blank=True, on_delete=models.SET_NULL)

    objects = StaffManager()

    class Meta:
        verbose_name = 'B 员工'
        verbose_name_plural = 'B 员工'
        db_table = 'hosp_staff'

    def has_project_approver_group_perm(self, ):
        group = self.organ.get_specified_group(GROUP_CATE_PROJECT_APPROVER)
        return self.has_group_perm(group)


class Doctor(Staff):
    """
    医生数据模型. 子类和父类都产生表结构, 而子表仅存储额外的属性字段
    """
    medical_title = models.CharField('医生职称', choices=DOCTOR_TITLE_CHOICES, max_length=3, null=True, blank=True)

    class Meta:
        verbose_name = 'D 医生'
        verbose_name_plural = 'D 医生'
        db_table = 'hosp_doctor'


class Group(BaseGroup):
    """
    机构权限组数据模型. 每个权限组有一个归属的企业
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', on_delete=models.CASCADE, null=True, blank=True)

    objects = GroupManager()

    class Meta:
        verbose_name = '权限组'
        verbose_name_plural = '权限组'
        db_table = 'perm_group'








