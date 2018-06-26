# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from django.db import transaction
from rest_framework.exceptions import NotFound
from utils import eggs
from nmis.hospitals.models import Hospital, Department, Staff, Doctor, Group
from organs.forms import OrganSignupForm
from base.forms import BaseForm
from nmis.hospitals.consts import DPT_ATTRI_CHOICES


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
            staff = new_organ.create_staff(**{
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
            new_organ.create_department(name='默认')
            return new_organ


class StaffSignupForm(BaseForm):
    """
    新增员工表单数据验证
    """
    ERR_CODES = {
        'err_username': '用户名为空或格式错误',
        'err_username_existed': '用户名已存在',
        'err_password': '密码为空或格式错误',
        'err_staff_name': '员工姓名错误',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                 '无效邮箱',
        'err_staff_title': '职位名为空或格式错误',
        'err_group_is_null': '权限组为空或数据错误',
        'err_group_not_exist': '权限组不存在',
    }

    def __init__(self, organ, dept, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ
        self.dept = dept

    def is_valid(self):
        is_valid = True
        # 校验必输项
        if not self.check_username() or not self.check_password() or not self.check_staff_name():
            is_valid = False

        # 校验非必输项
        if self.data.get('email') and not self.check_email():
            is_valid = False

        if self.data.get('contact_phone') and not self.check_contact_phone():
            is_valid = False

        if self.data.get('group_id') and not self.check_group():
            is_valid = False

        return is_valid

    def check_username(self):
        """校验用户名/账号
        """
        username = self.data.get('username', '').strip()
        if not username:
            self.update_errors('username', 'err_username')
            return False

        if User.objects.filter(username=username):
            self.update_errors('username', 'err_username_existed')
            return False

        return True

    def check_password(self):
        """校验密码"""
        password = self.data.get('password', '').strip()
        if not password:
            self.update_errors('password', 'err_password')
            return False
        return True

    def check_staff_name(self):
        """校验员工名称
        """
        staff_name = self.data.get('staff_name', '').strip()
        if not staff_name:
            self.update_errors('staff_name', 'err_staff_name')
            return False
        return True

    def check_email(self):
        """校验邮箱
        """
        email = self.data.get('email', '').strip()
        if not eggs.is_email_valid(email):
            self.update_errors('email', 'err_email')
            return False
        return True

    def check_contact_phone(self):
        """校验手机号
        """
        contact_phone = self.data.get('contact_phone', '').strip()
        if not eggs.is_phone_valid(contact_phone):
            self.update_errors('contact_phone', 'err_contact_phone')
            return False
        return True

    def check_staff_title(self):
        """校验职位名称"""
        staff_title = self.data.get('staff_title', '').strip()
        if not staff_title:
            self.update_errors('staff_title', 'err_staff_title')
            return False

        return True

    def check_group(self):
        group_id = self.data.get('group_id')
        if not group_id:
            self.update_errors('group_id', 'err_group_is_null')
            return False
        group = Group.objects.get_by_id(group_id)
        if not group:
            self.update_errors('group_id', 'err_group_not_exist')
            return False
        self.data.update({'group': group})

        return True

    def save(self):
        data = {
            'name': self.data.get('staff_name', '').strip(),
            'title': self.data.get('staff_title', '').strip(),
            'contact': self.data.get('contact_phone', '').strip(),
            'email': self.data.get('email', '').strip(),
        }

        user_data = {
            "username": self.data.get('username', '').strip(),
            "password": self.data.get('password', '').strip()
        }

        return Staff.objects.create_staff(self.organ, self.dept, user_data, **data)


class StaffUpdateForm(BaseForm):

    ERR_CODES = {
        'err_staff_name': '员工姓名错误',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                 '无效邮箱',
        'err_dept':                   '科室信息错误',
        'err_staff_title': '职位名为空或格式错误'
    }

    def __init__(self, staff, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, ** kwargs)
        self.staff = staff
        if data.get('staff_name'):
            self.data.update({'name': data.get('staff_name', '').strip()})
        if data.get('staff_title'):
            self.data.update({'title': data.get('staff_title', '').strip()})
        if data.get('contact_phone'):
            self.data.update({'contact': data.get('contact_phone', '').strip()})
        if data.get('email'):
            self.data.update({'email': data.get('email', '').strip()})

    def is_valid(self):
        is_valid = True
        if self.data.get('staff_name') and not self.check_staff_name():
            is_valid = False
        if self.data.get('email') and not self.check_email():
            is_valid = False
        if self.data.get('contact_phone') and not self.check_contact_phone():
            is_valid = False

        return is_valid

    def check_staff_name(self):
        """校验员工名称
        """
        staff_name = self.data.get('staff_name', '').strip()
        if not staff_name:
            self.update_errors('staff_name', 'err_staff_name')
            return False
        return True

    def check_email(self):
        """校验邮箱
        """
        email = self.data.get('email', '').strip()
        if not eggs.is_email_valid(email):
            self.update_errors('email', 'err_email')
            return False
        return True

    def check_contact_phone(self):
        """校验手机号
        """
        contact_phone = self.data.get('contact_phone', '').strip()
        if not eggs.is_phone_valid(contact_phone):
            self.update_errors('contact_phone', 'err_contact_phone')
            return False
        return True

    def check_staff_title(self):
        """校验职位名称"""
        staff_title = self.data.get('staff_title', '').strip()
        if not staff_title:
            self.update_errors('staff_title', 'err_staff_title')
            return False

        return True

    def save(self):
        update_staff = self.staff.update(self.data)
        update_staff.cache()
        return update_staff


class DepartmentUpdateFrom(BaseForm):
    """
    对修改科室信息进行表单验证
    """
    def __init__(self, dept, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.dept = dept

        self.ERR_CODES.update({
            'dept_name_err':        '科室名字不符合要求',
            'dept_contact_err':     '科室电话号码格式错误',
            'dept_attri_err':       '科室属性错误',
            'dept_desc_err':        '科室描述存在敏感字符',
        })

    def is_valid(self):
        if not self.check_contact() and not self.check_name() and not self.check_attri() and \
                not self.check_desc():
            return False
        return True

    def check_contact(self):
        contact = self.data.get('contact')
        if not contact:
            return True

        if not eggs.is_phone_valid(contact):
            self.update_errors('dept_contact', 'err_dept_contact')
            return False

        return True

    def check_name(self):
        name = self.data.get('name')
        return True

    def check_desc(self):
        desc = self.data.get('desc')
        return True

    def check_attri(self):
        attri = self.data.get('attri')

        if not attri in dict(DPT_ATTRI_CHOICES).keys():
            self.update_errors('attri', 'err_dept_attri')
            return False
        return True

    def save(self):
        data = {}
        name = self.data.get('name', '').strip()
        contact = self.data.get('contact', '').strip()
        attri = self.data.get('attri', '').strip()
        desc = self.data.get('desc', '').strip()

        if name:
            data['name'] = name
        if contact:
            data['contact'] = contact
        if attri:
            data['attri'] = attri
        if desc:
            data['desc'] = desc

        updated_dept = self.dept.update(data)
        updated_dept.cache()
        return updated_dept


class DepartmentCreateForm(BaseForm):
    def __init__(self, hospital, data, *args, **kwargs):
        BaseForm.__init__(self, data, hospital, *args, **kwargs)
        self.hospital = hospital

        self.ERR_CODES.update({
            'err_dept_name': '科室名字不符合要求',
            'dept_exist':     '同名科室已存在',
            'err_dept_contact': '科室电话号码格式错误',
            'err_dept_attri': '科室属性错误',
            'err_dept_desc': '科室描述存在敏感字符',
        })

    def is_valid(self):
        if not self.check_contact() or not self.check_name() or not self.check_attri() or \
                not self.check_desc():
            return False
        return True

    def check_contact(self):
        contact = self.data.get('contact')
        if not contact:
            return True
        if not eggs.is_phone_valid(contact):
            self.update_errors('dept_contact', 'err_dept_contact')
            return False
        return True

    def check_name(self):
        dept = Department.objects.filter(name=self.data.get('name'))
        if dept:
            self.update_errors('dept_name', 'dept_exist')
            return False
        return True

    def check_desc(self):
        # desc = self.data.get('desc')
        return True

    def check_attri(self):
        attri = self.data.get('attri')

        # 验证科室属性是否存在DPT_ATTRI_CHOICES中
        # attri dict(DPT_ATTRI_CHOICES)

        if not attri in dict(DPT_ATTRI_CHOICES).keys():
            self.update_errors('attri', 'err_dept_attri')
            return False
        return True

    def save(self):

        dept_data = {
            'name': self.data.get('name', '').strip(),
            'contact': self.data.get('contact', '').strip(),
            'desc': self.data.get('desc').strip(),
            'attri': self.data.get('attri').strip(),
        }

        try:
            new_dept = self.hospital.create_department(**dept_data)
            new_dept.cache()
            return new_dept
        except Exception as e:
            logging.exception(e)
            return None
