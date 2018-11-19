# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
import re

from django.contrib.auth.models import Permission
from django.db import transaction
from utils import eggs
from nmis.hospitals.models import Hospital, Department, Staff, Role
from organs.forms import OrganSignupForm
from base.forms import BaseForm
from nmis.hospitals.consts import ROLE_CATE_NORMAL, ROLE_CODE_NORMAL_STAFF, DPT_ATTRI_OTHER

from users.models import User


logger = logging.getLogger(__name__)


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

            # create admin staff for the new organ
            staff = new_organ.create_staff(**{
                'user': creator,
                'organ': new_organ,

                'name': contact_name,
                'title': contact_title,
                'contact': contact_phone,
                'email': email,
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
        'username_existed':         '用户名已存在',
        'username_out_of_bounds':   '用户名长度不能大于30个字符',
        'err_password':             '密码为空或格式错误',
        'staff_name_out_of_bounds': '员工姓名长度不能大于30个字符',
        'err_staff_name':           '员工姓名为空或数据错误',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                '无效邮箱',
        'err_staff_title':          '职位名称为空或格式错误',
        'staff_title_out_of_bounds': '职位名称长度不能大于30个字符',
        'role_not_exists':           '系统尚未设置角色, 请先维护',
    }

    def __init__(self, organ, dept, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ
        self.dept = dept

    def is_valid(self):
        is_valid = True
        # 校验必输项
        if not self.check_username() or not self.check_password() \
                or not self.check_staff_name() or not self.check_role_exists():
            is_valid = False

        # 校验非必输项
        if self.data.get('email') and not self.check_email():
            is_valid = False

        if self.data.get('contact_phone') and not self.check_contact_phone():
            is_valid = False

        if self.data.get('staff_title') and not self.check_staff_title():
            is_valid = False

        return is_valid

    def check_username(self):
        """校验用户名/账号
        """
        if self.data.get('username'):
            if not isinstance(self.data.get('username'), str):
                self.update_errors('username', 'err_username')
                return False
            username = self.data.get('username').strip()
            if not username:
                self.update_errors('username', 'err_username')
                return False
            if len(username) > 30:
                self.update_errors('username', 'username_out_of_bounds')
                return False
            if User.objects.filter(username=username):
                self.update_errors('username', 'username_existed')
                return False
            return True

    def check_password(self):
        """校验密码"""
        if self.data.get('password'):
            if not isinstance(self.data.get('password'), str):
                self.update_errors('password', 'err_password')
                return False
            password = self.data.get('password').strip()
            if not password:
                self.update_errors('password', 'err_password')
                return False
            return True

    def check_staff_name(self):
        """校验员工名称
        """
        if self.data.get('staff_name'):
            if not isinstance(self.data.get('staff_name'), str):
                self.update_errors('staff_name', 'err_staff_name')
                return False
            staff_name = self.data.get('staff_name', '').strip()
            if not staff_name:
                self.update_errors('staff_name', 'err_staff_name')
                return False
            if len(staff_name) > 30:
                self.update_errors('staff_name', 'staff_name_out_of_bounds')
                return False
            return True

    def check_email(self):
        """校验邮箱
        """
        if self.data.get('email'):
            if not isinstance(self.data.get('email'), str):
                self.update_errors('email', 'err_email')
                return False
            email = self.data.get('email').strip()
            if not eggs.is_email_valid(email):
                self.update_errors('email', 'err_email')
                return False
            return True

    def check_contact_phone(self):
        """校验手机号
        """
        contact_phone = self.data.get('contact_phone')
        if contact_phone:
            if not isinstance(contact_phone, str):
                self.update_errors('contact_phone', 'err_contact_phone')
                return False
            if not eggs.is_phone_valid(str(contact_phone).strip()):
                self.update_errors('contact_phone', 'err_contact_phone')
                return False
            return True

    def check_staff_title(self):
        """校验职位名称"""
        if self.data.get('staff_title'):
            if not isinstance(self.data.get('staff_title'), str):
                self.update_errors('staff_title', 'err_staff_title')
                return False
            staff_title = self.data.get('staff_title').strip()
            if not staff_title:
                self.update_errors('staff_title', 'err_staff_title')
                return False
            if len(staff_title) > 30:
                self.update_errors('staff_title', 'staff_title_out_of_bounds')
                return False
            return True

    def check_role_exists(self):
        from nmis.hospitals.models import Role
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_NORMAL_STAFF)
        if not role:
            self.update_errors('role', 'role_not_exists')
            return False
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
        'err_staff_name':           '员工姓名为空或数据错误',
        'staff_name_out_of_bounds': '员工姓名长度不能大于30个字符',
        'err_contact_phone':        '联系电话格式错误',
        'err_email':                '无效邮箱',
        'err_dept':                 '科室信息错误',
        'err_staff_title':          '职位名称为空或格式错误',
        'staff_title_out_of_bounds': '职位名称长度不能大于30个字符',
    }

    def __init__(self, staff, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, ** kwargs)
        self.staff = staff

    def is_valid(self):
        is_valid = True
        if self.data.get('staff_name') and not self.check_staff_name():
            is_valid = False
        if self.data.get('email') and not self.check_email():
            is_valid = False
        if self.data.get('contact_phone') and not self.check_contact_phone():
            is_valid = False
        if self.data.get('staff_title') and not self.check_staff_title():
            is_valid = False

        return is_valid

    def check_staff_name(self):
        """校验员工名称
        """
        if self.data.get('staff_name'):
            if not isinstance(self.data.get('staff_name'), str):
                self.update_errors('staff_name', 'err_staff_name')
                return False
            staff_name = self.data.get('staff_name').strip()
            if not staff_name:
                self.update_errors('staff_name', 'err_staff_name')
                return False
            if len(staff_name) > 30:
                self.update_errors('staff_name', 'staff_name_out_of_bounds')
                return False
            return True

    def check_email(self):
        """校验邮箱
        """
        if self.data.get('email'):
            if not isinstance(self.data.get('email'), str):
                self.update_errors('email', 'err_email')
                return False
            email = self.data.get('email').strip()
            if not eggs.is_email_valid(email):
                self.update_errors('email', 'err_email')
                return False
            return True

    def check_contact_phone(self):
        """校验手机号
        """
        contact_phone = self.data.get('contact_phone')
        if contact_phone:
            if not eggs.is_phone_valid(str(contact_phone).strip()):
                self.update_errors('contact_phone', 'err_contact_phone')
                return False
            return True

    def check_staff_title(self):
        """校验职位名称"""
        staff_title = self.data.get('staff_title')
        if staff_title:
            if not isinstance(staff_title, str):
                self.update_errors('staff_title', 'err_staff_title')
                return False
            if not staff_title.strip():
                self.update_errors('staff_title', 'err_staff_title')
                return False
            if len(staff_title.strip()) > 30:
                self.update_errors('staff_title', 'staff_title_out_of_bounds')
                return False
        return True

    def save(self):
        update_data = {
            'name': self.data.get('staff_name', '').strip(),
            'title': self.data.get('staff_title', '').strip(),
            'contact_phone': str(self.data.get('contact_phone', '')).strip(),
            'email': self.data.get('email', '').strip(),
            'dept': self.data.get('dept')
        }
        update_staff = self.staff.update(update_data)
        update_staff.clear_cache()
        return update_staff


class StaffBatchUploadForm(BaseForm):

    ERR_CODES = {
        'empty_username':               '第{0}行用户名不能为空或数据错误',
        'duplicate_username':           '第{0}行和第{1}行用户名重复，请检查',
        'username_exists':              '第{0}行用户名{1}已存在',
        'empty_staff_name':             '第{0}行员工姓名不能为空或数据错误',
        'err_contact_phone':            '第{0}联系电话格式错误',
        'empty_contact_phone':          '第{0}联系电话不能为空或数据错误',
        'err_email':                    '第{0}无效邮箱',
        'empty_email':                  '第{0}行邮箱不能为空或数据错误',
        'duplicate_email':              '第{0}行和第{1}行邮箱重复，请检查',
        'empty_dept_name':              '第{0}行科室信息不能为空或数据错误',
        'dept_not_exists':              '含有不存在的科室信息',
        'role_not_exists':              '系统尚未设置角色信息，请先维护'
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
            usernames, staff_names, dept_names, emails, contact_phones = [], [], [], [], []
            for item in sheet_data:
                usernames.append(item.get('username'))
                staff_names.append(item.get('staff_name'))
                dept_names.append(item.get('dept_name'))
                emails.append(item.get('email'))
                contact_phones.append(item.get('contact_phone'))
            pre_data['usernames'] = usernames
            pre_data['staff_names'] = staff_names
            pre_data['dept_names'] = dept_names
            pre_data['emails'] = emails
            pre_data['contact_phones'] = contact_phones
        return pre_data

    def is_valid(self):
        if self.check_username() and self.check_staff_name() and self.check_dept() \
                and self.check_email() and self.check_contact_phone() and self.check_role_exists():
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
        if not usernames:
            self.update_errors('username', 'empty_username', str(2))
            return False
        for i, username in enumerate(usernames):
            if not username:
                self.update_errors('username', 'empty_username', str(i + 2))
                return False
            if not isinstance(username, str):
                self.update_errors('username', 'empty_username', str(i + 2))
                return False
            if not username.strip():
                self.update_errors('username', 'empty_username', str(i + 2))
                return False
        usernames_tmp = usernames.copy()
        for i, username in enumerate(usernames):
            for j in range(i + 1, len(usernames_tmp)):
                if username == usernames_tmp[j]:
                    self.update_errors('username', 'duplicate_username', str(i + 2), str(j + 2))
                    return False

        users = User.objects.filter(username__in=usernames)
        if users:
            self.update_errors('username', 'username_exists', str(i + 2), users[0].username)
            return False

        return True

    def check_staff_name(self):
        """
        校验员工名称
        """
        staff_names = self.pre_data.get('staff_names')
        if not staff_names:
            self.update_errors('staff_name', 'empty_staff_name', str(2))
            return False
        for i, item in enumerate(staff_names):
            if not item:
                self.update_errors('staff_name', 'empty_staff_name', str(i+2))
                return False
            if not isinstance(item, str):
                self.update_errors('staff_name', 'empty_staff_name', str(i+2))
                return False
            if not item.strip():
                self.update_errors('staff_name', 'empty_staff_name', str(i+2))
                return False
        return True

    def check_email(self):
        """
        校验邮箱 非必输项
        """
        emails = self.pre_data.get('emails')
        if emails:
            emails_tmp = emails.copy()
            for i, item in enumerate(emails):
                if item:
                    if not isinstance(item, str):
                        self.update_errors('email', 'err_email', str(i+2))
                        return False
                    if not eggs.is_email_valid(item.strip()):
                        self.update_errors('email', 'err_email', str(i+2))
                        return False
                for j in range(i + 1, len(emails_tmp)):
                    if item and item == emails_tmp[j]:
                        self.update_errors('email', 'duplicate_email', str(i + 2), str(j + 2))
                        return False
            return True

    def check_contact_phone(self):
        """
        校验手机号
        """
        contact_phones = self.pre_data.get('contact_phones')
        if not contact_phones:
            self.update_errors('contact_phone', 'empty_contact_phone', str(2))
        for i, item in enumerate(contact_phones):
            if not item:
                self.update_errors('contact_phone', 'empty_contact_phone', str(i + 2))
                return False
            if not eggs.is_phone_valid(str(item).strip()):
                self.update_errors('contact_phone', 'err_contact_phone', str(i+2))
                return False
        return True

    def check_dept(self):
        """校验职位名称"""
        dept_names = self.pre_data.get('dept_names')
        if not dept_names:
            self.update_errors('dept', 'empty_dept_name', str(2))
            return False
        db_dept_names = Department.objects.values_list('name')

        for i, item in enumerate(dept_names):
            if not item:
                self.update_errors('dept', 'empty_dept_name', str(i + 2))
                return False
            if not isinstance(item, str):
                self.update_errors('dept', 'empty_dept_name', str(i + 2))
                return False
            if not item.strip():
                self.update_errors('dept', 'empty_dept_name', str(i + 2))
                return False
            if (item.strip(), ) not in db_dept_names:
                self.update_errors('dept', 'dept_not_exists', str(i + 2))
                return False
        return True

    def check_role_exists(self):
        from nmis.hospitals.models import Role
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_NORMAL_STAFF)
        if not role:
            self.update_errors('role', 'role_not_exists')
            return False
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
                    'contact_phone': str(row_data.get('contact_phone', '')).strip(),
                    'email': row_data.get('email', '').strip(),
                    'dept_name': row_data.get('dept_name', '').strip(),  # 将username和dept建立字典关系, 以便于批量查询dept
                    'organ': self.organ,
                })

            # 建立字典结构, 以便通过dept_name快速定位dept对象: key/value: dept_name/dept
            dept_dict = {}
            dept_name_set = set([dept_name.strip() for dept_name in self.pre_data['dept_names']])
            depts = Department.objects.filter(name__in=dept_name_set)
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
            'empty_dept_name':      '科室名称为空或数据错误',
            'dept_name_err':        '科室名字不符合要求',
            'dept_contact_err':     '科室电话号码格式错误',
            'dept_attri_err':       '科室属性错误',
            'dept_desc_err':        '科室描述存在敏感字符',
            'dept_name_out_of_bounds': '科室名称不能大于30个字符',
            'dept_exists':          '同名科室已存在',
            'err_dept_contact':     '科室电话号码格式错误',
            'empty_desc':           '科室描述为空或数据错误',
            'desc_out_of_bounds':   '科室描述不能大于100个字符',
        })

    def is_valid(self):
        if not self.check_contact() or not self.check_name() or not self.check_desc():
            return False
        return True

    def check_contact(self):
        contact = self.data.get('contact')
        if not contact:
            return True
        if not eggs.is_phone_valid(str(contact).strip()):
            self.update_errors('dept_contact', 'err_dept_contact')
            return False
        return True

    def check_name(self):
        name = self.data.get('name')
        if not name:
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if not isinstance(name, str):
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if not name.strip():
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if len(name.strip()) > 30:
            self.update_errors('dept_name', 'dept_name_out_of_bounds')
            return False
        db_dept = Department.objects.filter(name=name.strip()).first()
        if db_dept and not name == self.dept.name and name == db_dept.name:
            self.update_errors('dept_name', 'dept_exists')
            return False
        return True

    def check_desc(self):
        desc = self.data.get('desc')
        return True

    # def check_attri(self):
    #     attri = self.data.get('attri')
    #
    #     if not attri in dict(DPT_ATTRI_CHOICES).keys():
    #         self.update_errors('attri', 'err_dept_attri')
    #         return False
    #     return True

    def check_desc(self):
        desc = self.data.get('desc')
        if not desc:
            return True
        if not isinstance(desc, str):
            self.update_errors('desc', 'empty_desc')
            return False
        if not desc.strip():
            return True
        if len(desc.strip()) > 100:
            self.update_errors('desc', 'desc_out_of_bounds')
            return False
        return True

    def save(self):
        data = {}
        name = self.data.get('name', '')

        contact = self.data.get('contact', '')
        attri = self.data.get('attri', '')
        desc = self.data.get('desc', '')

        if name:
            data['name'] = name.strip()
        if contact:
            data['contact'] = str(contact).strip()
        if attri:
            data['attri'] = attri.strip()
        if desc:
            data['desc'] = desc.strip()

        updated_dept = self.dept.update(data)
        updated_dept.cache()
        return updated_dept


class DepartmentCreateForm(BaseForm):
    def __init__(self, hospital, data, *args, **kwargs):
        BaseForm.__init__(self, data, hospital, *args, **kwargs)
        self.hospital = hospital

        self.ERR_CODES.update({
            'empty_dept_name': '科室名称为空或数据错误',
            'dept_name_out_of_bounds': '科室名称不能大于30个字符',
            'dept_exists':     '同名科室已存在',
            'err_dept_contact': '科室电话号码格式错误',
            'err_dept_attri': '科室属性错误',
            'err_dept_desc': '科室描述存在敏感字符',
            'empty_desc': '科室描述为空或数据错误',
            'desc_out_of_bounds': '科室描述不能大于100个字符',
        })

    def is_valid(self):
        if not self.check_contact() or not self.check_name() or not self.check_desc():
            return False
        return True

    def check_contact(self):
        contact = self.data.get('contact')
        if not contact:
            return True
        if not eggs.is_phone_valid(str(contact).strip()):
            self.update_errors('dept_contact', 'err_dept_contact')
            return False
        return True

    def check_name(self):
        name = self.data.get('name')
        if not name:
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if not isinstance(name, str):
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if not name.strip():
            self.update_errors('dept_name', 'empty_dept_name')
            return False
        if len(name.strip()) > 30:
            self.update_errors('dept_name', 'dept_name_out_of_bounds')
            return False
        dept = Department.objects.filter(name=name.strip())
        if dept:
            self.update_errors('dept_name', 'dept_exists')
            return False
        return True

    def check_desc(self):
        desc = self.data.get('desc')
        if not desc:
            return True
        if not isinstance(desc, str):
            self.update_errors('desc', 'empty_desc')
            return False
        if not desc.strip():
            return True
        if len(desc.strip()) > 100:
            self.update_errors('desc', 'desc_out_of_bounds')
            return False
        return True

    def save(self):

        dept_data = {
            'name': self.data.get('name', '').strip(),
            'desc': self.data.get('desc', '').strip(),
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
        'organ_name_empty': '第{0}行所属机构为空或数据错误',
        'organ_name_exists': '第{0}行所属机构已存在',
        'error_attri': '第{0}行科室属性为空或数据错误',
        'dept_name_duplicate': '第{0}行和第{1}行科室名称重复，请检查',
        'dept_name_exists': '科室{}已存在',
        'dept_name_empty': '第{0}行科室名称为空或数据错误',
        'dept_name_out_of_bounds': '第{0}科室名称不能大于30个字符',
        'desc_empty': '第{0}行职能描述为空数据错误',
        'desc_out_of_bounds': '第{0}行职能描述不能大于100个字符',

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
                dept_names.append(sheet_data[i].get('dept_name'))
            for i in range(len(sheet_data)):
                # dept_attris.append(sheet_data[i].get('dept_attri'))
                dept_attris.append(DPT_ATTRI_OTHER)
            for i in range(len(sheet_data)):
                descs.append(sheet_data[i].get('desc'))
        pre_data['dept_names'] = dept_names
        pre_data['dept_attris'] = dept_attris
        pre_data['descs'] = descs
        return pre_data

    def is_valid(self):
        if not self.check_dept() or not self.check_dept_desc():
            return False
        return True

    def check_dept(self):
        """校验科室名称"""
        dept_names = self.pre_data['dept_names']
        if not dept_names:
            self.update_errors('dept', 'dept_name_empty', str(2))
            return False
        dept_name_set = set(dept_names)
        dept_query_set = Department.objects.filter(name__in=dept_name_set)
        for index, dept_name in enumerate(dept_names):
            if not dept_name:
                self.update_errors('dept', 'dept_name_empty', str(index+2))
                return False
            if not isinstance(dept_name, str):
                self.update_errors('dept', 'dept_name_empty', str(index+2))
                return False
            if not dept_name.strip():
                self.update_errors('dept', 'dept_name_empty', str(index+2))
                return False
            if len(dept_name.strip()) > 30:
                self.update_errors('dept', 'dept_name_out_of_bounds', str(index+2))
                return False
            if dept_name in [dept.name for dept in dept_query_set]:
                self.update_errors('dept', 'organ_name_exists', str(index+2))
                return False
        return True

    # def check_dept_attri(self):
    #     """
    #     校验科室属性
    #     """
    #     emails = self.pre_data['emails']
    #     for i in range(len(emails)):
    #         if emails[i]:
    #             if not eggs.is_email_valid(emails[i]):
    #                 self.update_errors('email', 'err_email', str(i + 2))
    #                 return False
    #     return True
    #
    # def check_contact_phone(self):
    #     """
    #     校验部门联系电话
    #     """
    #     contact_phones = self.pre_data['contact_phones']
    #     if not contact_phones:
    #         return True
    #     for i, phone in enumerate(contact_phones):
    #         if phone:
    #             if not eggs.is_phone_valid(str(phone).strip()):
    #                 self.update_errors('contact_phone', 'err_contact_phone', str(i + 2))
    #                 return False
    #     return True

    def check_dept_desc(self):
        """
        校验部门职能描述
        """
        desc_list = self.pre_data['descs']
        if not desc_list:
            self.update_errors('desc', 'desc_empty', str(2))
            return False
        for i, desc in enumerate(desc_list):
            if desc:
                if not isinstance(desc, str):
                    self.update_errors('desc', 'desc_empty', str(i + 2))
                    return False
                if len(desc.strip()) > 100:
                    self.update_errors('desc', 'desc_out_of_bounds', str(i + 2))
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
                    'name': row_data.get('dept_name', '').strip(),
                    'attri': row_data.get('dept_attri', ''),
                    'desc': row_data.get('desc', '').strip(),
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
            'role_name_out_of_bounds': '角色名称不能大于30个字符',
            'permission_error': '权限数据为空或错误',
            'permission_not_exists': '数据中含有不存在的权限'
        })

    def is_valid(self):
        if not self.check_role_name() or not self.check_permission():
            return False
        return True

    def check_role_name(self):
        name = self.data.get('name')
        if not name:
            self.update_errors('name', 'role_name_error')
            return False
        if not isinstance(name, str):
            self.update_errors('name', 'role_name_error')
            return False
        if not name.strip():
            self.update_errors('name', 'role_name_error')
            return False
        if len(name.strip()) > 30:
            self.update_errors('name', 'role_name_out_of_bounds')
            return False
        db_role = Role.objects.filter(name=name.strip())
        if db_role:
            self.update_errors('name', 'role_name_exists')
            return False
        return True

    def check_permission(self):
        perm_keys = self.data.get('permissions')
        if not perm_keys or len(perm_keys) <= 0:
            self.update_errors('permissions', 'permission_error')
            return False
        permissions = Permission.objects.filter(id__in=perm_keys)
        if not permissions or len(permissions) < len(perm_keys):
            self.update_errors('permissions', 'permission_not_exists')
            return False
        return True

    def save(self):
        role_data = {'cate': ROLE_CATE_NORMAL}
        if self.data.get('name'):
            role_data['name'] = self.data.get('name').strip()
        if self.data.get('codename'):
            role_data['codename'] = self.data.get('codename').strip()
        if self.data.get('desc'):
            role_data['desc'] = self.data.get('desc').strip()
        permissions = Permission.objects.filter(id__in=self.data.get('permissions'))
        role_data['permissions'] = permissions
        return Role.objects.create_role_with_permissions(role_data)


class RoleUpdateForm(BaseForm):

    def __init__(self, old_role, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.old_role = old_role
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'role_name_error': '角色名称为空或数据错误',
            'role_name_exists': '角色已存在',
            'role_name_out_of_bounds': '角色名称不能大于30个字符',
            'permission_error': '权限数据为空或错误',
            'permission_not_exists': '数据中含有不存在的权限'
        })

    def is_valid(self):
        return self.check_role_name() and self.check_permission()

    def check_role_name(self):
        name = self.data.get('name')
        if not name:
            self.update_errors('name', 'role_name_error')
            return False
        if not isinstance(name, str):
            self.update_errors('name', 'role_name_error')
            return False
        if not name.strip():
            self.update_errors('name', 'role_name_error')
            return False
        if len(name.strip()) > 30:
            self.update_errors('name', 'role_name_out_of_bounds')
            return False
        db_role = Role.objects.filter(name=name.strip()).first()
        if db_role and not name.strip() == self.old_role.name and name.strip() == db_role.name:
            self.update_errors('name', 'role_name_exists')
            return False
        return True

    def check_permission(self):
        perm_keys = self.data.get('permissions')
        if not perm_keys or len(perm_keys) <= 0:
            self.update_errors('permissions', 'permission_error')
            return False
        permissions = Permission.objects.filter(id__in=perm_keys)
        if not permissions or len(permissions) < len(perm_keys):
            self.update_errors('permissions', 'permission_not_exists')
            return False
        return True

    def save(self):
        role_data = {'cate': ROLE_CATE_NORMAL}
        if not self.data.get('name') or not self.data.get('codename') or not self.data.get('permissions'):
            return None
        if self.data.get('name'):
            role_data['name'] = self.data.get('name').strip()
        if self.data.get('codename'):
            role_data['codename'] = self.data.get('codename').strip()
        if self.data.get('desc'):
            role_data['desc'] = self.data.get('desc').strip()
        permissions = Permission.objects.filter(id__in=self.data.get('permissions'))
        role_data['permissions'] = permissions
        try:
            new_role = self.old_role.update(role_data)
            new_role.cache()
            return new_role
        except Exception as e:
            logger.exception(e)
            return None

