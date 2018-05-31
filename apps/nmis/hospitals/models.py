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
from organs.models import BaseOrgan, BaseStaff, BaseDepartment, BaseGroup

logs = logging.getLogger(__name__)


class Hospital(BaseOrgan):
    """
    医疗机构数据模型
    """

    class Meta:
        verbose_name = u'A 医疗机构'
        verbose_name_plural = u'A 医疗机构'
        db_table = 'hospitals_hospital'


class Department(BaseDepartment):
    """
    医疗机构下设科室数据模型
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医疗机构')

    class Meta:
        verbose_name = u'A 科室/部门'
        verbose_name_plural = u'A 科室/部门'
        db_table = 'hospitals_department'

    def __str__(self):
        return u'%s' % self.name


class Staff(BaseStaff):
    """
    医疗机构一般员工(非医生)
    """

    # 一个员工仅属于一个企业
    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', null=True, blank=True)
    dept = models.ForeignKey(Department, verbose_name=u'所属科室/部门', null=True, blank=True)

    class Meta:
        verbose_name = 'B 员工'
        verbose_name_plural = 'B 员工'
        db_table = 'hospitals_staff'


class Doctor(Staff):
    """
    医生数据模型. 子类和父类都产生表结构
    """

    class Meta:
        verbose_name = 'D 医生'
        verbose_name_plural = 'D 医生'
        db_table = 'hospitals_doctor'


class Group(BaseGroup):
    """
    机构权限组数据模型. 每个权限组有一个归属的企业
    """

    GROUP_DOCTOR = 'DC'

    GROUP_CATE_CHOICES = (
        (GROUP_DOCTOR, u'医生'),
    )

    GROUP_CATE_DICT = dict(GROUP_CATE_CHOICES)

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', null=True, blank=True)

    class Meta:
        verbose_name = '权限组'
        verbose_name_plural = '权限组'
        db_table = 'perm_group'








