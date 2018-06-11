# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from base.forms import BaseForm

from django.db import transaction
from nmis.hospitals.models import Hospital
from organs.forms import OrganSignupForm

from users.models import User
from nmis.hospitals.models import Department
from utils import eggs

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


class DepartmentUpdateFrom(BaseForm):
    """
    对修改科室信息进行表单验证
    """
    def __init__(self, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.data = data

        self.ERR_CODES.update({
            'department_contact_error': '科室电话号码格式错误',
            'department_name': '科室名字不符合要求',
            'department_attri': '科室属性错误',
            'department_desc': '科室描述存在敏感字符',
        })

    def is_valid(self):

        return self.check_contact()

    def check_contact(self):
        contact = self.data.get('contact')
        if not contact:
            return True
        elif not eggs.is_phone_valid(contact):
            self.errors.update({'contact': self.ERR_CODES['department_contact_error']})
            return False
        return True

    def check_name(self):
        pass

    def check_desc(self):
        pass

    def check_attri(self):
        pass

    def save(self):
        data = {}
        if self.data.get('name'):
            data['name'] = self.data.get('name')
        if self.data.get('contact'):
            data['contact'] = self.data.get('contact')
        if self.data.get('desc'):
            data['desc'] = self.data.get('desc')
        if self.data.get('attri'):
            data['attri'] = self.data.get('attri')
        return Department.objects.update(**data)
