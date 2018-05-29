#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from django.db import transaction

from utils import eggs
from base.forms import BaseForm
from users.forms import UserLoginForm
from users.models import User

from .models import Organ

logs = logging.getLogger(__name__)


PASSWORD_COMPILE = re.compile(r'^\w{6,18}$')


class OrganSignupForm(BaseForm):
    """
    对企业注册信息进行表单验证
    """

    ERR_CODES = {
        'invalid_email':        u'无效的Email',
        'user_existed':         u'Email已注册',
        'email_existed':        u'您所在的企业已在使用"行云HR",请联系管理员将您加入团队，或者您也可以申请独立试用系统',
        'err_password':         u"密码只能为6-18位英文字符或下划线组合",

        'err_organ_name':       u'企业名称错误',
        'err_organ_scale':      u'企业规模错误',
        'err_contact_name':     u'联系人姓名填写错误',
        'err_contact_phone':    u'联系人电话填写错误',
        'err_contact_title':    u'联系人职位填写错误',

        'params_lack':          u'参数缺乏',
    }

    def __init__(self, req, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.req = req
        self.errors = {}

    def is_valid(self):
        valid_email = self.check_email()
        valid_organ_name = self.check_organ_name()
        valid_organ_scale = self.check_organ_scale()
        valid_contact_name = self.check_contact_name()
        valid_contact_phone = self.check_contact_phone()
        valid_contact_title = self.check_contact_title()

        return valid_email and valid_organ_name \
            and valid_organ_scale and valid_contact_name \
            and valid_contact_phone and valid_contact_title

    def save(self):
        email = self.data.get('email')

        organ_name = self.data.get('organ_name')
        organ_scale = self.data.get('organ_scale')

        contact_name = self.data.get('contact_name')
        contact_phone = self.data.get('contact_phone')
        contact_title = self.data.get('contact_title')

        with transaction.atomic():  # 事务原子操作
            creator = User.objects.create_param_user(('email', email),
                is_active=False
            )

            # create organ
            new_organ = Organ.objects.create_organ(**{
                'creator':       creator,
                'organ_name':    organ_name,
                'organ_scale':   int(organ_scale) if organ_scale else 1,
                'contact_name':  contact_name,
                'contact_phone': contact_phone,
                'contact_title': contact_title
            })

            new_organ.init_default_groups()

            # create admin staff for the new organ
            staff = Organ.objects.create_staff(**{
                'user': creator,
                'organ': new_organ,

                'name': contact_name,
                'title': contact_title,
                'contact': contact_phone,
                'email': email,
                'group': new_organ.get_admin_group()
            })
            # Folder.objects.get_or_create_system_folder(organ=new_organ) # 依赖错误!!!

            # create default department
            Organ.objects.create_department(**{  # TODO: create method考虑放到organ对象中...
                'organ':    new_organ,
                'name':     u'默认'
            })

            return new_organ

    def check_email(self):
        """ 检查注册Email

        检查项如下:
        1. 格式是否正确
        2. 是否已存在该邮箱账号
        3. 是否有相同后缀的邮箱用户已通过申请
        """
        email = self.data.get('email', '').strip()
        if not email or not eggs.is_email_valid(email):
            self.errors.update({'email': self.ERR_CODES['invalid_email']})
            return False

        try:
            user = User.objects.get(email=email)
            self.errors.update({'email': self.ERR_CODES['user_existed']})
            return False
        except User.DoesNotExist:
            pass
        return True

    def check_contact_name(self):
        contact_name  = self.data.get('contact_name', '').strip()
        if not contact_name:
            self.errors.update({'contact_name': self.ERR_CODES['err_contact_name']})
            return False
        return True

    def check_contact_phone(self):
        contact_phone = self.data.get('contact_phone', '').strip()
        if not contact_phone or not eggs.is_phone_valid(contact_phone):
            self.errors.update(
                {'contact_phone': self.ERR_CODES['err_contact_phone']}
            )
            return False

        return True

    def check_contact_title(self):
        contact_title  = self.data.get('contact_title', '').strip()
        if not contact_title:
            self.errors.update(
                {'contact_title': self.ERR_CODES['err_contact_title']}
            )
            return False
        return True

    def check_organ_name(self):
        organ_name = self.data.get('organ_name', '').strip()
        if not organ_name:
            self.errors.update(
                {'organ_name': self.ERR_CODES['err_organ_name']}
            )
            return False
        return True

    def check_organ_scale(self):
        organ_scale  = self.data.get('organ_scale', 1)
        if not organ_scale:
            self.errors.update(
                {'organ_scale': self.ERR_CODES['err_organ_scale']}
            )
            return False
        return True


class OrganLoginForm(UserLoginForm):
    """ 企业管理员登录表单验证 """

    def __init__(self, req, data=None, *args, **kwargs):
        super(UserLoginForm, self).__init__(self, req, data, *args, **kwargs)

        # 企业管理员额外增加的验证异常类型
        self.ERR_CODES.update({
            'not_organ_admin':      u'无企业管理员权限',
            'email_auth_checking':  u'Email正在审核',
            'email_auth_failed':    u'Email未通过审核',
        })

    def is_valid(self):
        super_form = self.super_form()
        organ_admin = self.organ_admin()
        email_auth_check = self.email_auth_check()
        email_auth_failed = self.email_auth_failed()

        return super_form and organ_admin and email_auth_check and email_auth_failed

    def super_form(self):
        if not super(OrganLoginForm, self).is_valid():
            return False
        return True

    def organ_admin(self):
        if not self.user_cache.organ:
            self.update_errors('email', 'not_organ_admin')
            return False
        return True

    def email_auth_check(self):
        if self.user_cache.organ.is_checking():
            self.update_errors('email', 'email_auth_checking')
            return False
        return True

    def email_auth_failed(self):
        if self.user_cache.organ.is_auth_failed():
            self.update_errors('email', 'email_auth_failed')
            return False
        return True
