 # coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
组织/机构相关数据模型
"""

import logging

from django.db import models, transaction

from base.models import BaseModel
from nmis.hospitals.managers import GroupManager, RoleManager, SequenceManager

from organs.models import BaseOrgan, BaseStaff, BaseDepartment, BaseGroup
from users.models import User
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

    def __str__(self):
        return '%s %s' % (self.id, self.organ_name)

    def save(self, *args, **kwargs):  # 重写save函数，当admin后台保存表单后，更新缓存
        super(self.__class__, self).save(*args, **kwargs)
        self.cache()

    def get_all_flows(self):
        from nmis.projects.models import ProjectFlow
        return ProjectFlow.objects.filter(organ=self)

    ################################################
    #                   科室与员工管理
    ################################################

    def get_all_depts(self):
        """
        返回科室所有列表
        """
        return Department.objects.filter(organ=self).order_by('id')

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

    def get_staffs(self, dept=None, search_key=None):
        """
        返回机构的员工列表（根据员工名称关键字模糊查询）
        :param dept: 科室, Department object
        :param search_key: 员工名字关键字
        """
        staffs_queryset = Staff.objects.filter(organ=self).order_by('id')
        if search_key:
            staffs_queryset = staffs_queryset.filter(name__contains=search_key)
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

    def assign_roles_dept_domains(self, users, roles, depts):
        old_ships = []
        ship_args = []
        same_ships = []
        for user in users:
            for role in roles:
                ship_args.append(UserRoleShip(user=user, role=role))

            old_ship_query = UserRoleShip.objects.filter(user=user).all()
            if old_ship_query:
                for query in old_ship_query:
                    old_ships.append(query)

        for ship_arg in ship_args[:]:
            for old_ship in old_ships[:]:
                if ship_arg.user.id == old_ship.user.id and ship_arg.role.id == old_ship.role.id:
                    ship_args.remove(ship_arg)
                    same_ships.append(old_ship)
                    old_ships.remove(old_ship)
        try:
            with transaction.atomic():

                if ship_args:
                    for ship in ship_args:
                        ship.save()
                        ship.cache()
                        ship.dept_domains.set(depts)
                if old_ships:
                    for ship in old_ships:
                        ship.clear_cache()
                        ship.dept_domains.set(depts)
                        ship.delete()
                if same_ships:
                    for s in same_ships:
                        s.dept_domains.set(depts)
                        s.cache
                return True
        except Exception as e:
            logs.info(e.__cause__)
            logs.exception(e)
            return False

    def create_department(self, **dept_data):
        return Department.objects.create(organ=self, **dept_data)

    def batch_upload_departments(self, depts_data):
        try:
            with transaction.atomic():
                dept_list = []
                for data in depts_data:
                    dept_list.append(
                        Department(
                            organ=data.get('organ'),
                            name=data.get('name'),
                            attri=DPT_ATTRI_MEDICAL,
                            desc=data.get('desc')
                    ))
            Department.objects.bulk_create(dept_list)
            return True
        except Exception as e:
            logging.exception(e)
            return False


class Department(BaseDepartment):
    """
    医疗机构下设科室数据模型
    """

    organ = models.ForeignKey(Hospital, verbose_name=u'所属医疗机构', on_delete=models.CASCADE, related_name='organ')  # 重写父类
    attri = models.CharField('科室/部门属性', choices=DPT_ATTRI_CHOICES, max_length=2, null=True, blank=True)

    class Meta:
        verbose_name = u'B 科室/部门'
        verbose_name_plural = u'B 科室/部门'
        db_table = 'hosp_department'

    VALID_ATTRS = [
        'name', 'contact', 'attri', 'desc'
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)


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
        'name', 'title', 'organ', 'dept', 'contact', 'email', 'status'
    ]

    class Meta:
        verbose_name = 'C 员工'
        verbose_name_plural = 'C 员工'
        permissions = (
            ('view_staff', 'can view staffs'),
        )
        db_table = 'hosp_staff'

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def has_project_dispatcher_perm(self, ):
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


class Role(BaseModel):
    """
    角色数据模型
    """
    name = models.CharField('角色名称', max_length=40)
    codename = models.CharField('角色代码', max_length=100, unique=False, null=True, blank=True, default='')
    cate = models.CharField('类别', max_length=4, choices=GROUP_CATE_CHOICES,
                            null=False, blank=True)
    permissions = models.ManyToManyField(
        Group, verbose_name='权限集',
        related_name="roles", related_query_name='role',
        blank=True
    )
    desc = models.CharField('描述', max_length=100, null=True, blank=True, default='')
    users = models.ManyToManyField(
        User, verbose_name='角色所属用户集',
        through='hospitals.UserRoleShip', through_fields=('role', 'user'),
        related_name="roles", related_query_name='role',
        blank=True
    )
    objects = RoleManager()

    class Meta:
        verbose_name = '角色'
        verbose_name_plural = '角色'
        db_table = 'perm_role'

    def __str__(self):
        return u'%s' % self.name

    def set_permissions(self, perms):
        """
        为角色设置权限集
        """
        self.permissions.set(perms)
        self.save()

    def add_permission(self, perm):
        """
        角色内新加权限
        :param perm: 权限对象,
        """
        self.permissions.set(perm)

    def get_permissions(self):
        """获取去角色下的权限"""
        return self.permissions.all()

    def get_user_role_ships(self, user=None):
        """
        获取用户角色关系记录
        :param user:
        :return:
        """
        return UserRoleShip.objects.filter(user=user, role=self).all()

    def get_user_role_dept_domains(self, user):
        """
        获取用户当前角色可操作的部门域
        :param user:
        :return:
        """
        if not user:
            return None
        return UserRoleShip.objects.filter(user=user, role=self).first().dept_domains.all()


class UserRoleShip(BaseModel):
    user = models.ForeignKey(
        'users.User', verbose_name='用户',
        related_name='user_role_ships', on_delete=models.CASCADE,
    )
    role = models.ForeignKey(
        'hospitals.Role', verbose_name='角色',
        related_name='user_role_ships', on_delete=models.CASCADE,
    )
    dept_domains = models.ManyToManyField(
        Department, verbose_name='用户当前角色可操作部门域集合',
        related_name="user_role_ships", related_query_name='user_role_ship', blank=True
    )

    class Meta:
        verbose_name = '用户角色关系'
        verbose_name_plural = verbose_name
        unique_together = ('user', 'role')
        db_table = 'perm_user_roles'

    def __str__(self):
        return '%s %s' % (self.user_id, self.role_id)


class HospitalAddress(BaseModel):
    """
    医院内部地址
    """
    title = models.CharField('名称', max_length=128)
    type = models.CharField('类型', choices=HOSPITAL_AREA_TYPE_CHOICES, max_length=3)
    parent = models.ForeignKey('self', verbose_name='父级地址', on_delete=models.PROTECT, null=True, blank=True)
    # 祖节点到当节点的父节点最短路径, 由各节点id的字符串组成，每个id,之间用‘-’进行分隔
    parent_path = models.CharField('父地址路径', max_length=1024, default='', null=False, blank=False)
    level = models.SmallIntegerField('层级')
    sort = models.SmallIntegerField('排序')
    disabled = models.BooleanField('是否禁用', default=False,)
    dept = models.ForeignKey(
        'hospitals.Department', verbose_name='所属科室', on_delete=models.PROTECT,
        null=True, blank=True
    )

    desc = models.CharField('描述', max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = '医院内部地址'
        verbose_name_plural = verbose_name
        db_table = 'hosp_hospital_address'

    VALID_ATTRS = [
        'title', 'type', 'parent', 'parent_path', 'level', 'sort', 'disabled', 'dept', 'desc',
    ]

    def __str__(self):
        return '%d' % (self.id, )


class Sequence(BaseModel):
    """
    序列数据模型
    可用于各业务编码或表ID
    """
    seq_code = models.CharField('sequence编码', max_length=16, unique=True, default='2')
    seq_name = models.CharField('sequence编码名称', max_length=64)
    seq_value = models.IntegerField('sequence值', default=0)
    increment = models.IntegerField('步进', default=1)
    remark = models.CharField('备注', max_length=64, null=True, blank=True)

    objects = SequenceManager()

    class Meta:
        verbose_name = '序列'
        verbose_name_plural = verbose_name
        db_table = 'hosp_sequence'

    VALID_ATTRS = [
        'seq_code', 'seq_name', 'seq_value', 'increment', 'remark',
    ]

    def __str__(self):
        return '%d %s' % (self.id, self.seq_code)

    def curr_value(self):
        return self.seq_value

    def next_value(self):
        return self.seq_value + 1
