# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
组织/机构相关数据模型
"""

import logging

from django.db import models, transaction

import settings
from utils import times
from base.models import BaseModel
from users.models import UserSecureRecord

from .managers import OrganManager, PermissionManager, StaffManager

logger = logging.getLogger(__name__)


class BaseOrgan(BaseModel):
    """
    企业/组织机构抽象数据模型
    """

    AUTH_CHECKING = 1   # 等待审核...
    AUTH_APPROVED = 2   # 审核通过
    AUTH_FAILED = 3     # 审核失败

    # 机构认证审核状态选项
    AUTH_STATUS_CHOICES = (
        (AUTH_CHECKING, u'等待审核'),
        (AUTH_APPROVED, u'审核通过'),
        (AUTH_FAILED,   u'审核未通过'),
    )

    SCALE_CHOICES = (
        (1, '0-49人'),
        (2, '50-199人'),
        (3, '200-499人'),
        (4, '500-999人'),
        (5, '1000-1999人'),
        (6, '2000人以上'),
    )

    default_timeout = 60 * 60  # 默认在redis中缓存60分钟

    # 企业注册时的创建者. 创建者不可变并唯一, 企业管理员可以变化
    creator = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=u'创建者', on_delete=models.CASCADE)

    organ_name = models.CharField(u'企业/组织名称', max_length=100, default='')
    organ_scale = models.SmallIntegerField(u'企业规模', choices=SCALE_CHOICES, null=True, blank=True, default=1)

    contact_name = models.CharField(u'联系人姓名', max_length=32, default='')
    contact_phone = models.CharField(u'联系人手机号码', max_length=20, null=True, blank=True, default='') # 不作为登录手机号
    contact_title = models.CharField(u'联系人职位', max_length=40, null=True, blank=True, default='')

    logo = models.CharField(u'企业logo', max_length=80, blank=True, null=True, default='')
    industry = models.CharField(u'行业类型', max_length=80, null=True, blank=True, default='')
    address = models.CharField(u'企业/机构地址', max_length=100, null=True, blank=True, default='')
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')

    auth_status = models.SmallIntegerField(u'认证状态', choices=AUTH_STATUS_CHOICES, default=AUTH_CHECKING)

    # 各报道链接以逗号分隔
    media_cover = models.CharField(u'媒体报道', max_length=800, null=True, blank=True, default='')
    desc = models.TextField(u'企业介绍', null=True, blank=True, default='')

    objects = OrganManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s %s' % (self.id, self.organ_name)

    def is_authed(self):
        """
        是否已审核通过
        """
        return self.auth_status == self.AUTH_APPROVED

    def is_auth_failed(self):
        """是否审核失败"""
        return self.auth_status == self.AUTH_FAILED

    def is_checking(self):  # 是否等待审核中
        return self.auth_status == self.AUTH_CHECKING

    def accept(self):
        """通过审核"""
        self.auth_status = self.AUTH_APPROVED
        self.save()
        self.cache()

    def show_auth_status(self):
        """ 显示审核状态 """
        if self.is_authed():
            return u'审核通过'
        if self.auth_status == self.AUTH_CHECKING:
            return u'审核中'
        if self.auth_status == self.AUTH_FAILED:
            return u'审核未通过'

    def create_staff(self, user, name, email, contact, group=None, title=''):
        """
        创建员工对象
        :param user: 关联用户
        :param name: 员工姓名
        :param title:  员工职位
        :param contact: 联系电话
        :param email: Email
        :return:
        """
        kwargs = {
            'user': user,
            'organ': self,
            'name': name,
            'title': title,
            'contact': contact,
            'email': email,
            'group': group,
        }
        staff = BaseStaff(**kwargs)
        staff.save()
        return staff

    ################################################
    #                  权限组操作
    ################################################

    def get_all_groups(self):
        pass

    def get_specified_group(self, group_key):
        """
        通过权限组关键字获取指定的权限组
        :param group_key: 权限组关键字, 对应group模型中的cate, 字符串类型
        :return: 对应的权限组对象, Group object
        """
        return self.get_all_groups().filter(cate=group_key).first()

    def get_admin_group(self):
        """
        返回企业管理员组. 每个企业当且仅有一个admin组
        """
        return self.get_all_groups().filter(is_admin=True).first()


    ################################################
    #                  员工操作
    ################################################

    def get_all_staffs(self):
        """获取企业所有员工列表"""
        return BaseStaff.objects.custom_filter(organ=self)

    def get_staffs_in_group(self, group):
        return self.get_all_staffs().filter(group=group)


class CommonOrgan(BaseOrgan):
    """
    通用/一般的企业/组织机构数据模型. 企业/机构相关数据逻辑的默认实现, 若企业/机构数据没有特殊性,
    可考虑采用该默认数据模型

    """

    class Meta:
        verbose_name = u'A 企业/组织'
        verbose_name_plural = u'A 企业/组织'
        db_table = 'organs_organ'


class BaseDepartment(BaseModel):
    """
    企业的部门数据模型
    """

    organ = models.ForeignKey(BaseOrgan, verbose_name=u'所属医疗机构', on_delete=models.CASCADE)
    name = models.CharField(u'部门名称', max_length=100, default='')
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')
    desc = models.TextField(u'描述', null=True, blank=True, default='')

    class Meta:
        abstract = True

    def __str__(self):
        return u'%s' % self.name


class BaseStaff(BaseModel):
    """
    企业员工数据模型
    """
    DELETE_STATUS = 'D'
    NORMAL_STATUS = 'N'
    STAFF_STATUS = (
        (DELETE_STATUS, u'删除'),
        (NORMAL_STATUS, u'正常')
    )

    default_timeout = 60 * 60  # 默认在redis中缓存60分钟

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=u'用户账号', on_delete=models.CASCADE)
    organ = models.ForeignKey(BaseOrgan, verbose_name=u'所属机构', null=True, blank=True, on_delete=models.CASCADE)
    dept = models.ForeignKey(BaseDepartment, verbose_name=u'所属部门', null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(u'名字', max_length=40, null=True, blank=True, default='')
    title = models.CharField(u'职位名称', max_length=40, null=True, blank=True, default='') # 后续或可考虑扩展成对象
    contact = models.CharField(u'联系电话', max_length=20, null=True, blank=True, default='')
    email = models.EmailField(u'Email', null=True, blank=True, default='')  # 非账号email

    # # 一个staff仅可以加入一个权限group
    # group = models.ForeignKey('organs.Group', verbose_name=u'权限组', null=True, blank=True, on_delete=models.SET_NULL)

    status = models.CharField(u'员工状态', max_length=1, default=NORMAL_STATUS)

    objects = StaffManager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s, %s' % (self.id, self.name)
    #
    # def is_organ_admin(self):
    #     """是否为所属企业的管理员"""
    #     return self.organ.get_admin_group() == self.group
    #
    # def is_admin_for_organ(self, organ):
    #     """
    #     是否为指定企业的管理员
    #     """
    #     return self.organ == organ and self.is_organ_admin()
    #
    # def set_group(self, group):
    #     """
    #     给员工设置权限组
    #     :param group: Group object
    #     """
    #     self.group = group
    #     self.save()
    #
    # def has_group_perm(self, group):
    #     """
    #     员工是否拥有所属企业指定某权限组的权限
    #     :return:
    #     """
    #     if not group.organ == self.organ:
    #         return False
    #
    #     return self.is_organ_admin() or group == self.group
    #
    # def get_group_permissions(self, obj=None):  # TODO: 权限组及权限可以考虑从cache中读取
    #     """
    #     返回权限码列表. 若传入obj, 则仅返回与obj匹配的权限码列表
    #     """
    #     if self.is_organ_admin():
    #         return Permission.objects.values_list(['codename'])
    #
    #     return Permission.objects.filter(group__in=self.groups).values('codename')
    #
    # def has_perm(self, perm, obj=None):
    #     """
    #     :param perm: 权限codename字符串
    #     """
    #     return True if perm in self.get_group_permissions() else False
    #
    # def has_perms(self, perm_list, obj=None):
    #     """
    #     """
    #     for perm in perm_list:
    #         if not self.has_perm(perm, obj):
    #             return False
    #     return True

    def get_secure_key(self):
        """
        对于登录账号未激活的企业员工用户, 需要该secure_key以访问系统
        若存在可用key, 则直接返回. 否则新生成key返回
        :return:
        """
        secure_record = StaffSecureRecord.objects.filter(
            user=self.user, is_used=False, expire_datetime__gt=times.now()
        ).first()
        if secure_record:
            return secure_record.key
        return self.user.generate_secure_record(StaffSecureRecord, expire_hours=7*24).key

    def set_delete(self):
        """删除员工,标记未已删除"""
        self.user.is_active = False
        self.user.save()
        self.status = self.DELETE_STATUS
        self.save()
        self.user.clear_cache()
        self.clear_cache()

    def add_to_organ(self, name, contact, organ, group):
        """用于恢复删除用户操作"""
        self.name = name
        self.contact = contact
        self.organ = organ
        self.group = group
        self.status = self.NORMAL_STATUS
        self.save()


class StaffSecureRecord(UserSecureRecord):
    """非登录企业员工key相关信息"""
    pass


class Permission(BaseModel):
    """
    自定义权限数据模型
    """

    name = models.CharField(u'权限名', max_length=255)
    codename = models.CharField(u'权限码', max_length=100)
    pre_defined = models.BooleanField(u'平台预定义', default=False)

    objects = PermissionManager()

    class Meta:
        verbose_name = '权限'
        verbose_name_plural = '权限'
        db_table = 'perm_permission'
        ordering = ('codename', )


class BaseGroup(BaseModel):
    """
    权限组数据模型. 每个权限组有一个归属的企业
    """

    GROUP_CATE_CHOICES = ()

    organ = models.ForeignKey('organs.BaseOrgan', verbose_name=u'所属企业', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(u'权限组名', max_length=40)
    cate = models.CharField(u'权限组类别', max_length=4, choices=GROUP_CATE_CHOICES, null=True, blank=True)
    is_admin = models.BooleanField(u'管理员组', default=False)

    permissions = models.ManyToManyField(Permission, verbose_name=u'权限集', blank=True)
    desc = models.CharField(u'描述', max_length=100, null=True, blank=True, default='')

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'%s' % self.name

    def set_permissions(self, perms):
        """
        为权限组初始化设置权限集
        """
        pass

    def add_permission(self, perm):
        """
        权限组内新加权限
        :param perm: 权限对象,
        """
        pass



