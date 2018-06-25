# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
组织/机构相关数据模型
"""

import logging

from django.db import models, transaction

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

    def save(self, *args, **kwargs):  # 重写save函数，当admin后台保存表单后，更新缓存
        super(self.__class__, self).save(*args, **kwargs)
        self.cache()

    def get_all_flows(self):
        from nmis.projects.models import ProjectFlow
        return ProjectFlow.objects.filter(hospital=self)

    ################################################
    #                   科室与员工管理
    ################################################

    def get_all_depts(self):
        """ 返回医院的所有科室 """
        return Department.objects.filter(organ=self)

    def add_dept(self, dept):
        """
        添加科室
        :param dept:
        :return:
        """
        pass

    def create_dept(self, **dept_data):
        """
        创建新科室
        :param dept_data: dict data
        :return:
        """
        pass

    def delete_dept(self):
        pass

    def add_staff_to_dept(self, staff, dept):
        """
        添加某员工到指定科室
        :param staff:
        :param dept:
        :return:
        """
        pass

    def create_staff(self, dept, **staff_data):
        """
        创建新员工
        :param staff: dict data
        :param dept:
        :return:
        """
        return Staff.objects.create_staff(self, dept, **staff_data)

    def get_staffs(self, dept=None):
        """
        返回机构的员工列表
        :param dept: 科室, Department object
        """
        staffs_queryset = Staff.objects.filter(organ=self)
        return staffs_queryset.filter(dept=dept) if dept else staffs_queryset


    ################################################
    #                  权限组操作
    ################################################

    def get_all_groups(self):
        """返回企业的所有权限组"""
        return Group.objects.filter(organ=self)

    def create_group(self, **kwargs):
        """
        创建权限组
        :param kwargs: 输入参数
        :return:
        """
        return Group.objects.create_group(self, **kwargs)

    def init_default_groups(self):
        """
        机构初建时初始化默认权限组
        :return:
        """

        group_list = []
        for k in GROUP_CATE_DICT.keys():
            group_data = {'is_admin': False, 'commit': False}
            group_data.update(GROUPS.get(k))
            group_list.append(
                self.create_group(**group_data)
            )
        with transaction.atomic():
            self.create_admin_group()
            Group.objects.bulk_create(group_list)

    def create_admin_group(self):
        """创建管理员组"""
        if self.get_admin_group():
            logs.warn('Create Error: admin group existed for organ: %s' % self.id)
            return

        group_data = {'is_admin': True}
        group_data.update(GROUPS.get('admin'))
        return self.create_group(**group_data)

    def create_department(self, **dept_data):
        return Department.objects.create(organ=self, **dept_data)


class Department(BaseDepartment):
    """
    医疗机构下设科室数据模型
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医疗机构', on_delete=models.CASCADE,  related_name='organ')  # 重写父类
    attri = models.CharField('科室/部门属性', choices=DPT_ATTRI_CHOICES, max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = u'B 科室/部门'
        verbose_name_plural = u'B 科室/部门'
        db_table = 'hosp_department'

    VALID_ATTRS = [
        'name', 'contact', 'attri', 'desc'
    ]

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

    VALID_ATTRS = [
        'name', 'title', 'organ', 'dept', 'contact', 'email', 'group', 'status'
    ]

    class Meta:
        verbose_name = 'C 员工'
        verbose_name_plural = 'C 员工'
        db_table = 'hosp_staff'

    def has_project_approver_perm(self, ):
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
    group_cate_choices = GROUP_CATE_CHOICES

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医院', on_delete=models.CASCADE, null=True, blank=True)
    cate = models.CharField(u'权限组类别', max_length=4, choices=GROUP_CATE_CHOICES,
                            null=True, blank=True)
    objects = GroupManager()

    class Meta:
        verbose_name = '权限组'
        verbose_name_plural = '权限组'
        db_table = 'perm_group'








