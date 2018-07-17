# coding=utf-8
#
# Created by junn, on 16/11/29
#

"""
用户/权限相关模型
"""

import base64
import datetime
import logging

from base.models import BaseModel
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, User
from django.core.signing import TimestampSigner
from django.db import models
from django.utils.timezone import now

from utils import eggs, images
from base.authtoken import CustomToken
from users.managers import UserManager

logs = logging.getLogger(__name__)

signer = TimestampSigner()
sign = lambda string: base64.b64encode(signer.sign(string))
unsign = lambda signed: signer.unsign(base64.b64decode(signed))


ACCT_TYPE_CHOICES = (
    ('E', u'显式注册'),  # 正常流程注册
    ('I', u'邀请注册'),  # 被邀请形式隐式注册
    ('O', u'第3方登录注册')
)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    """
    用户数据基础模型.
    可用username/phone/email其中之一进行注册/登录. 注册后另外2个属性可继续绑定并作为登录账号(需加登录标识).
    """

    MALE = 'M'
    FEMALE = 'F'
    UNKNOWN = 'U'

    GENDER_CHOICES = (
        (MALE, u'男'),
        (FEMALE, u'女'),
        (UNKNOWN, u'未知'),
    )

    username = models.CharField(u'用户名', max_length=255, blank=True, unique=True, null=True, default='')
    email = models.EmailField(u'Email', blank=True, null=True, default='')
    phone = models.CharField(u'手机号', max_length=25, blank=True, null=True, default='')

    is_staff = models.BooleanField(u'职员状态', default=False)
    is_active = models.BooleanField(u'是否激活', default=True)
    date_joined = models.DateTimeField(u'注册时间', auto_now_add=True)
    acct_type = models.CharField(u'账号类型', max_length=2, choices=ACCT_TYPE_CHOICES, default='E')  # 账号注册类型

    # 该字段仅存储文件名(不包括路径), 大图小图同名且以不同的路径区分
    avatar = models.CharField(u'头像', max_length=80, blank=True, null=True, default='')
    nickname = models.CharField(u'昵称', max_length=32, null=True, blank=True, default='')
    birth = models.DateField(u'生日', null=True, blank=True, auto_now_add=True)
    gender = models.CharField(u'性别', max_length=1, choices=GENDER_CHOICES, default='U')

    login_count = models.IntegerField(u'登录次数', default=0)
    last_login_ip = models.GenericIPAddressField(u'最后登录IP', null=True, blank=True)

    USERNAME_FIELD = 'username' # email
    VALID_AUTH_FIELDS = ['phone', 'email', 'username']  # 允许的可用于注册/登录的有效属性字段
    backend = 'base.backends.CustomizedModelBackend'
    roles = models.ManyToManyField('nmis.hospitals.models.Role', verbose_name='员工',
                                   related_name="users", related_query_name='user', blank=True)

    objects = UserManager()

    class Meta:
        app_label = 'users'
        db_table = 'users_user'
        swappable = 'AUTH_USER_MODEL'

        verbose_name = u'用户'
        verbose_name_plural = u'用户'

    def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.id

    def info(self):
        """输出用于log显示"""
        return u'%s, %s, %s' % (self.id, self.phone, self.email)

    def save_avatar(self, avatar_file):
        """保存头像文件到FS, 同时生成指定尺寸的小图"""

        self.avatar = images.save_image(
            avatar_file, eggs.gen_uuid1() + '.jpg',
            thumb_size=(90, 90), create_thumb=True, cate='avatar'
        )

    def get_avatar_path(self):  # 返回头像全路径
        if not self.avatar:
            return ''
        return '%s%s/%s' % (settings.MEDIA_URL, settings.USER_AVATAR_DIR['thumb'],
                            self.avatar)

    def handle_login(self, req):
        """ 登录及后续处理, 登录后将user对象缓存.
        :param req: django request请求对象
        """

        login(req, self)

        if 'HTTP_X_FORWARDED_FOR' in req.META.keys():
            self.last_login_ip = req.META['HTTP_X_FORWARDED_FOR']
        else:
            self.last_login_ip = req.META['REMOTE_ADDR']

        # self.incr_login_count()  # 登录次数+1
        self.save()
        self.cache()

    def get_authtoken(self):
        """ 返回登录鉴权token """

        try:
            token, created = CustomToken.objects.get_or_create(user=self)
            if not created and token.is_expired():  # 已存在的token若过期, 则刷新token
                token = CustomToken.refresh(token)
            return token.key if token else ''
        except Exception as e:
            logs.exception(e.message)
            return ''

    def get_profile(self):
        """
        get related Profile object, default name is 'profile'
        """
        if hasattr(self, '_cached_profile'):
            return self._cached_profile

        try:
            self._cached_profile = getattr(self, settings.USER_PROFILE, None)
            self.cache()
            return self._cached_profile
        except Exception as e:
            logs.exception(e)
            return None

    def generate_secure_record(self, klass, expire_hours):
        record = klass(user=self, key=sign(self.email), expire_datetime=now() + datetime.timedelta(hours=expire_hours))
        record.save()
        return record

    def generate_reset_record(self):
        return self.generate_secure_record(klass=ResetRecord, expire_hours=2)

    def get_roles(self):
        """获取用户拥有的角色"""
        return self.roles.all()

    def get_permissions(self):
        """获取用户拥有的权限"""
        user_perms = []
        for role in self.roles:
            for perm in role.get_permissions():
                if perm not in user_perms:
                    user_perms.append(perm)
        return user_perms

    def get_perm_domains(self):
        """获取用户可操作的权限域"""
        perm_domains = []
        for role in self.roles:
            for perm_domain in role.get_perm_domains():
                if perm_domain not in perm_domains:
                    perm_domains.append(perm_domain)
        return perm_domains



class UserSecureRecord(BaseModel):
    """
    针对一些特殊的未注册或账号未激活的权限请求, 增加该抽象模型类
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    key = models.CharField(max_length=128)
    expire_datetime = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def get_user(self):
        return self.user

    def expired(self):
        return now() >= self.expire_datetime

    def used(self):
        return bool(self.is_used)

    def is_valid(self):
        try:
            unsigned = unsign(self.key)
        except:
            return False
        return (not self.used()) and (not self.expired()) and (str(self.user.email) == unsigned)

    def set_invalid(self):
        self.is_used = True
        return self.save(update_fields=['is_used'])

    class Meta:
        abstract = True


class ResetRecord(UserSecureRecord):
    """帐号重置key相关信息"""
    pass




