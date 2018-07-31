# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from django.db import transaction
from utils import eggs
from nmis.hospitals.models import Hospital, Department, Staff, Group, Role
from organs.forms import OrganSignupForm
from base.forms import BaseForm
from nmis.hospitals.consts import DPT_ATTRI_CHOICES, GROUP_CATE_NORMAL_STAFF

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
        'err_username':             '用户名为空或格式错误',
        'err_username_existed':     '用户名已存在',
        'err_password':             '密码为空或格式错误',
        'err_staff_name':           '员工姓名错误',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                '无效邮箱',
        'err_staff_title':          '职位名为空或格式错误',
        'err_group_is_null':        '权限组为空或数据错误',
        'err_group_not_exist':      '权限组不存在',
    }

    def __init__(self, organ, dept, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ
        self.dept = dept

    def is_valid(self):
        is_valid = True
        # 校验必输项
        if not self.check_username() or not self.check_password() \
                or not self.check_staff_name() or not self.check_group():
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
        group = None
        if not group_id:
            group = Group.objects.filter(cate=GROUP_CATE_NORMAL_STAFF, is_admin=0).first()
            if not group:
                self.update_errors('group_id', 'err_group_not_exist')
            self.data.update({'group': group})
            return True
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
            'group': self.data.get("group")
        }

        user_data = {
            "username": self.data.get('username', '').strip(),
            "password": self.data.get('password', '').strip()
        }

        return Staff.objects.create_staff(self.organ, self.dept, user_data, **data)


class StaffUpdateForm(BaseForm):

    ERR_CODES = {
        'err_staff_name':           '员工姓名错误',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                '无效邮箱',
        'err_dept':                 '科室信息错误',
        'err_staff_title':          '职位名为空或格式错误'
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


class StaffBatchUploadForm(BaseForm):

    ERR_CODES = {
        'null_username':                '第{0}行用户名不能为空',
        'duplicate_username':           '第{0}行和第{1}行用户名重复，请检查',
        'username_exists':              '用户名{}已存在',
        'null_staff_name':              '第{0}行员工姓名不能为空',
        'err_contact_phone':            '第{0}联系电话格式错误',
        'err_email':                    '第{0}无效邮箱',
        'empty_dept_data':              '没有科室数据',
        'err_dept':                     '含有不存在的科室信息',
        'err_group_not_exist':          '系统不存在普通员工权限，请先维护'
    }

    def __init__(self, organ, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ
        self.group = None
        self.pre_data = self.init_data()

    def init_data(self):
        """
        封装各列数据, 以进行数据验证
        :return:
        """
        pre_data = {}
        if self.data and self.data[0] and self.data[0][0]:
            sheet_data = self.data[0]
            usernames, staff_names, dept_names, emails, contact_phones = [], [], [], [], []
            for i in range(len(sheet_data)):
                usernames.append(sheet_data[i].get('username', '').strip())
            for i in range(len(sheet_data)):
                staff_names.append(sheet_data[i].get('staff_name', '').strip())
            for i in range(len(sheet_data)):
                dept_names.append(sheet_data[i].get('dept_name', '').strip())
            for i in range(len(sheet_data)):
                emails.append(sheet_data[i].get('email', '').strip())
            for i in range(len(sheet_data)):
                contact_phones.append(str(sheet_data[i].get('contact_phone', '')).strip())
                pre_data['usernames'] = usernames
                pre_data['staff_names'] = staff_names
                pre_data['dept_names'] = dept_names
                pre_data['emails'] = emails
                pre_data['contact_phones'] = contact_phones
        return pre_data

    def is_valid(self):
        if self.check_username() and self.check_staff_name() and self.check_dept() \
                and self.check_email() and self.check_contact_phone() and self.check_group():
            return True
        return False

    def check_username(self):
        """
        校验用户名
        用户名非空校验
        用户名重复校验
        用户名已存在校验
        """
        usernames = self.pre_data.get('usernames')
        for i in range(len(usernames)):
            if not usernames[i]:
                self.update_errors('username', 'null_username', str(i + 2))
                return False

        for i in range(len(usernames)):
            usernames_tmp = usernames.copy()
            for j in range(i + 1, len(usernames_tmp)):
                if usernames[i] == usernames_tmp[j]:
                    self.update_errors('username', 'duplicate_username', str(i + 2), str(j + 2))
                    return False

        users = User.objects.filter(username__in=usernames)
        if users:
            self.update_errors('username', 'username_exists', users[0].username)
            return False

        return True

    def check_staff_name(self):
        """
        校验员工名称
        """
        staff_names = self.pre_data.get('staff_names')
        for i in range(len(staff_names)):
            if not staff_names[i]:
                self.update_errors('staff_name', 'null_staff_name', str(i+2))
                return False

        return True

    def check_email(self):
        """
        校验邮箱
        """
        emails = self.pre_data.get('emails')
        for i in range(len(emails)):
            if emails[i]:
                if not eggs.is_email_valid(emails[i]):
                    self.update_errors('email', 'err_email', str(i+2))
                    return False
        return True

    def check_contact_phone(self):
        """
        校验手机号
        """
        contact_phones = self.pre_data.get('contact_phones')
        for i in range(len(contact_phones)):
            if contact_phones[i]:
                if not eggs.is_phone_valid(str(contact_phones[i])):
                    self.update_errors('contact_phone', 'err_contact_phone', str(i+2))
                    return False

        return True

    def check_dept(self):
        """校验职位名称"""
        dept_names = self.pre_data.get('dept_names')
        if not dept_names:
            self.update_errors('dept', 'empty_dept_data')
            return False

        distincted_dept_names = set(dept_names)
        dept_query_set = Department.objects.filter(name__in=distincted_dept_names)
        if not dept_query_set or len(dept_query_set) < len(distincted_dept_names):
            self.update_errors('dept', 'err_dept')
            return False

        return True

    def check_group(self):
        group = Group.objects.filter(cate=GROUP_CATE_NORMAL_STAFF, is_admin=0).first()
        if not group:
            self.update_errors('group_id', 'err_group_not_exist')
        self.group = group
        return True

    def save(self):
        # 封装excel数据
        staffs_data = []
        if self.data and self.data[0] and self.data[0][0]:
            sheet_data = self.data[0]

            for row_data in sheet_data:
                staffs_data.append({
                    'username': row_data.get('username', '').strip(),
                    'staff_name': row_data.get('staff_name', '').strip(),
                    'contact_phone': row_data.get('contact_phone', '').strip(),
                    'email': row_data.get('email', '').strip(),
                    'dept_name': row_data.get('dept_name').strip(),  # 将username和dept建立字典关系, 以便于批量查询dept
                    'organ': self.organ,
                    'group': self.group
                })

            # 建立字典结构, 以便通过dept_name快速定位dept对象: key/value: dept_name/dept
            dept_dict = {}
            dept_names = set(self.pre_data['dept_names'])
            depts = Department.objects.filter(name__in=dept_names)
            for dept in depts:
                dept_dict[dept.name] = dept

            for staff in staffs_data:
                staff['dept'] = dept_dict[staff['dept_name']]
                del staff['dept_name']

        return Staff.objects.batch_upload_staffs(staffs_data)


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
        if not self.check_contact() or not self.check_name() or \
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

    def save(self):

        dept_data = {
            'name': self.data.get('name', '').strip(),
            'contact': self.data.get('contact', '').strip(),
            'desc': self.data.get('desc').strip(),
            'attri': 'OT'
        }

        try:
            new_dept = self.hospital.create_department(**dept_data)
            new_dept.cache()
            return new_dept
        except Exception as e:
            logging.exception(e)
            return None


class DepartmentBatchUploadForm(BaseForm):
    ERR_CODES = {
        'organ_name': '第{0}行所属机构为空或不存在',
        'error_attri': '第{0}行科室属性为空或数据错误',
        'dept_name_duplicate': '第{0}行和第{1}行科室名称重复，请检查',
        'dept_name_exists': '科室{}已存在',
        'err_dept': '第{0}行科室名称为空或数据错误',
        'desc_errr': '第{0}行职能描述数据错误'
    }

    def __init__(self, organ, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ
        self.pre_data = self.init_data()

    def init_data(self):
        """
        封装各列数据, 以进行数据验证
        :return:
        """
        pre_data = {}
        if self.data and self.data[0] and self.data[0][0]:
            sheet_data = self.data[0]
            dept_names, dept_attris, descs, = [], [], []
            for i in range(len(sheet_data)):
                dept_names.append(sheet_data[i].get('dept_name', '').strip())
            for i in range(len(sheet_data)):
                dept_attris.append(sheet_data[i].get('dept_attri', '').strip())
            for i in range(len(sheet_data)):
                descs.append(sheet_data[i].get('desc', '').strip())
        pre_data['dept_names'] = dept_names
        pre_data['dept_attris'] = dept_attris
        pre_data['descs'] = descs
        return pre_data

    def is_valid(self):
        # if self.check_username() and self.check_staff_name() and self.check_dept() \
        #         and self.check_email() and self.check_contact_phone():
        #     return True
        # return False
        return True


    def check_dept(self):
        """校验科室名称"""
        dept_names = self.pre_data['dept_names']
        if not dept_names:
            self.update_errors('dept', 'empty_dept_data')
            return False

        distincted_dept_names = set(dept_names)
        dept_query_set = Department.objects.filter(name__in=distincted_dept_names)
        if not dept_query_set or len(dept_query_set) < len(distincted_dept_names):
            self.update_errors('dept', 'err_dept')
            return False

        return True

    def check_dept_attri(self):
        """
        校验科室属性
        """
        emails = self.pre_data['emails']
        for i in range(len(emails)):
            if emails[i]:
                if not eggs.is_email_valid(emails[i]):
                    self.update_errors('email', 'err_email', str(i + 2))
                    return False
        return True

    def check_dept_desc(self):
        """
        校验只能描述
        """
        contact_phones = self.pre_data['contact_phones']
        for i in range(len(contact_phones)):
            if contact_phones[i]:
                if not eggs.is_phone_valid(str(contact_phones[i])):
                    self.update_errors('contact_phone', 'err_contact_phone', str(i + 2))
                    return False

        return True

    def save(self):
        # 封装excel数据
        depts_data = []
        if self.data and self.data[0] and self.data[0][0]:
            sheet_data = self.data[0]

            for row_data in sheet_data:
                depts_data.append({
                    'organ': self.organ,
                    'name': row_data.get('dept_name', ''),
                    'attri': row_data.get('dept_attri', ''),
                    'desc': row_data.get('desc', ''),
                })

        return self.organ.batch_upload_departments(depts_data)


class RoleCreateForm(BaseForm):

    def __init__(self, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'role_name_error': '角色名称为空或数据错误',
            'role_name_exists': '角色已存在',
            'permission_error': '权限数据为空或错误',
            'permission_not_exists': '数据中含有不存在的权限'
        })

    def is_valid(self):
        return self.check_role_name() and self.check_permission()

    def check_role_name(self):
        if not self.data.get('name', '').strip():
            self.update_errors('name', 'role_name_error')
            return False
        role = Role.objects.filter(name=self.data.get('name'))
        if role:
            self.update_errors('name', 'role_name_exists')
            return False
        return True

    def check_permission(self):
        perm_keys = self.data.get('permissions')
        if not perm_keys or len(perm_keys) <= 0:
            self.update_errors('permissions', 'permission_error')
            return False
        permissions = Group.objects.filter(id__in=perm_keys)
        if not permissions or len(permissions) < len(perm_keys):
            self.update_errors('permissions', 'permission_not_exists')
            return False
        return True

    def save(self):
        role_data = {
            'name': self.data.get('name', '').strip(),
            'codename': "",
            'cate': 'GCR',
            'desc': self.data.get('desc').strip(),
        }
        permissions = Group.objects.filter(id__in=self.data.get('permissions'))
        role_data['permissions'] = permissions
        return Role.objects.create_role(role_data)


class RoleUpdateForm(BaseForm):

    def __init__(self, old_role, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.old_role = old_role
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'role_name_error': '角色名称为空或数据错误',
            'role_name_exists': '角色已存在',
            'permission_error': '权限数据为空或错误',
            'permission_not_exists': '数据中含有不存在的权限'
        })

    def is_valid(self):
        return self.check_role_name() and self.check_permission()

    def check_role_name(self):
        if not self.data.get('name', '').strip():
            self.update_errors('name', 'role_name_error')
            return False
        role = Role.objects.filter(name=self.data.get('name'))
        if role:
            self.update_errors('name', 'role_name_exists')
            return False
        return True

    def check_permission(self):
        perm_keys = self.data.get('permissions')
        if not perm_keys or len(perm_keys) <= 0:
            self.update_errors('permissions', 'permission_error')
            return False
        permissions = Group.objects.filter(id__in=perm_keys)
        if not permissions or len(permissions) < len(perm_keys):
            self.update_errors('permissions', 'permission_not_exists')
            return False
        return True

    def save(self):
        role_data = {
            'name': self.data.get('name', '').strip(),
            'codename': "",
            'cate': 'GCR',
            'desc': self.data.get('desc').strip(),
        }
        permissions = Group.objects.filter(id__in=self.data.get('permissions'))
        role_data['permissions'] = permissions
        try:
            new_role = self.old_role.update(role_data)
            new_role.cache()
            return new_role
        except Exception as e:
            logs.exception(e)
            return None

