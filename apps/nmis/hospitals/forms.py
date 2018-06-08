# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from django.db import transaction
from utils import  eggs
from nmis.hospitals.models import Hospital
from organs.forms import OrganSignupForm
from base.forms import  BaseForm


from users.models import User


logs = logging.getLogger(__name__)


PASSWORD_COMPILE = re.compile(r'^\w{6,18}$')


class HospitalSignupForm(OrganSignupForm):
    """
    对医院注册信息进行表单验证
    """

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
            new_organ = Hospital.objects.create_hospital(**{
                'creator':       creator,
                'organ_name':    organ_name,
                'organ_scale':   int(organ_scale) if organ_scale else 1,
                'contact_name':  contact_name,
                'contact_phone': contact_phone,
                'contact_title': contact_title
            })

            new_organ.init_default_groups()

            # create admin staff for the new organ
            staff = Hospital.objects.create_staff(**{
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
            Hospital.objects.create_department(**{  # TODO: create method考虑放到organ对象中...
                'organ':    new_organ,
                'name':     u'默认'
            })

            return new_organ


class StaffSignupForm(BaseForm):
    """
    员工表单数据验证
    """
    ERR_CODES = {
        'err_contact_phone': u'联系电话错误',
        'invalid_email': u'无效邮箱',
        'err_name_not_null': u'员工姓名不能为空',
        'err_contact_not_null': u'联系电话不能为空',
    }

    def __init__(self, req, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.req = req
        self.errors = {}

    def is_valid(self):
        pass

    def check_username(self):
        """校验用户名/账号
        1.非空校验
        2.格式校验
        3.用户名是否已经注册

        :return:
        """
        pass

    def check_name(self):
        """校验员工名称
        1.非空校验
        2.格式校验
        :return:
        """

        name = self.data.get('name','').strip()
        if not name:
            self.errors.update({'name': self.ERR_CODES['err_name_not_null']})
            return False
        return True

    def check_email(self):
        """校验邮箱

        1.非空校验
        2.格式校验
        3.系统是否已经存在相同邮箱账号

        :return:
        """
        pass

    def check_contact_phone(self):
        """校验手机号

        1.非空校验
        2.格式校验
        3.手机号是否已经被其他用户绑定

        :return:
        """

        contact_phone = self.data.get('contact','').strip()
        if not contact_phone:
            self.errors.update(
                {'contact': self.ERR_CODES['err_contact_not_null']}
            )
            return False

        if not eggs.is_phone_valid(contact_phone):
            self.errors.update(
                {'contact': self.ERR_CODES['err_contact_format']}
            )
            return False

    def save(self):
        username = self.data.get('username')
        name = self.data.get('name')
        title = self.data.get('title')
        contact = self.data.get('contact')
        email = self.data.get('email')
        organ_id = self.data.get('organ_id')
        dept_id = self.data.get('dept_id')
        group_id = self.data.get('group_id')
        medical_title = self.data.get('medical_title')


        return None



 #'id', 'organ_id', 'dept_id', 'group_id', 'user_id', 'name', 'title','contact', 'email', 'status', 'created_time',

