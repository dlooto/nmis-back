# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging
from django.db import transaction
from django.db.models import Q, F

from nmis.hospitals.consts import ROLE_CODE_HOSP_SUPER_ADMIN, ROLES, ROLE_CODE_CHOICES, \
    ROLE_CODE_NORMAL_STAFF, SEQ_CODE_CHOICES, SEQUENCES
from settings import USER_DEFAULT_PWD
from users.models import User

from base.models import BaseManager
from utils import times

logger = logging.getLogger(__name__)


class HospitalManager(BaseManager):

    def create_hospital(self, **kwargs):
        """
         暂未实现
        """
        pass


class StaffManager(BaseManager):

    def create_staff(self, organ, dept, user_data, **data):
        """
        创建员工
        :param organ: 机构对象
        :param dept: 科室对象
        :param user_data: 用于创建user账号的dict数据
        :param data: 员工数据
        :return:
        """
        try:
            with transaction.atomic():
                user = User.objects.create_param_user(
                    ('username', user_data.get('username')), password=USER_DEFAULT_PWD, is_active=True,
                )
                from nmis.hospitals.models import Role
                role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_NORMAL_STAFF)
                if not role:
                    logger.warning('Error: normal staff role not exists')
                    return None
                user.set_roles([role, ])
                return self.create(organ=organ, dept=dept, user=user, **data)
        except Exception as e:
            logger.exception(e)
            return None

    def batch_upload_staffs(self, staffs_data):
        try:
            with transaction.atomic():
                user_list = []
                for data in staffs_data:
                    user = User(
                        username=data.get('username'),
                        is_active=True, is_staff=False, is_superuser=False,
                        last_login=times.now(), date_joined=times.now()
                    )
                    user.set_password(USER_DEFAULT_PWD)
                    user_list.append(user)
                none_id_users = User.objects.bulk_create(user_list)

                users = User.objects.filter(username__in=[user.username for user in none_id_users])
                from nmis.hospitals.models import Role
                role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_NORMAL_STAFF)
                for user in users:
                    user.set_roles([role])
                user_dict = {}
                for user in users:
                    user_dict[user.username] = user

                staff_list = []
                for data in staffs_data:
                    staff_list.append(
                        self.model(
                            organ=data.get('organ'), dept=data.get('dept'),
                            user=user_dict.get(data.get('username')),
                            name=data.get('staff_name'),
                            contact=data.get('contact_phone'),
                            email=data.get('email'),
                        )
                    )
                self.bulk_create(staff_list)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def get_by_name(self, organ, staff_name):
        """
        通过名字模糊查询返回员工列表
        :param organ:
        :param staff_name: 员工姓名
        :return:
        """
        return self.filter(organ=organ, name__contains=staff_name) if True else False

    def get_by_dept(self, organ, dept_id):
        """
        通过科室查询员工
        :param organ:
        :param dept_id: 当前机构科室id
        :return:
        """
        return self.filter(organ=organ, dept_id=dept_id)

    def get_count_by_dept(self, organ, dept):
        """
        通过科室查询科室人员数
        :param organ:
        :param dept:
        :return:
        """
        return self.filter(organ=organ, dept=dept).count()


class RoleManager(BaseManager):

    def create_role_with_permissions(self, data, commit=True, **kwargs):
        name = data.get("name", '')
        codename = data.get("codename", '')
        desc = data.get('desc', '')
        permissions = data.get('permissions', [])
        if not name or not codename or not permissions:
            logger.warning('Parameter Error: name, codename or permissions required')
            return None
        if self.filter(Q(codename=codename) | Q(name=name)):
            logger.warning('Create Error: role existed')
            return None
        role = self.model(name=name, codename=codename, desc=desc, **kwargs)
        try:
            if commit:
                role.save()
                role.permissions.set(permissions)
                role.cache()
            return role
        except Exception as e:
            logger.exception(e)
            return None

    def get_all_roles(self):
        """返回所有角色"""
        return self.all()

    def create_role(self, **kwargs):
        """
        创建角色
        """
        if not kwargs.get('name') or not kwargs.get('codename'):
            logger.warning('Parameter Error: name or codename required')
            return None
        if self.filter(Q(name=kwargs.get('name')) | Q(codename=kwargs.get('codename'))):
            logger.warning('Create Error: role existed')
            return None
        try:
            return self.create(**kwargs)
        except Exception as e:
            logger.exception(e)
            return None

    def get_role_by_keyword(self, **keyword):
        """
        通过关键字查询角色
        :param keyword: id, name 或 codename键值对
        :return:
        """
        if keyword.get('id'):
            return self.filter(id=keyword.get('id')).first()
        if keyword.get('name'):
            return self.filter(name=keyword.get('name')).first()
        if keyword.get('codename'):
            return self.filter(codename=keyword.get('codename')).first()
        return None

    def init_default_roles(self):
        """
        初始化默认角色
        :return:
        """

        role_list = []
        try:
            for k in dict(ROLE_CODE_CHOICES).keys():

                role = self.create_role(**ROLES.get(k))
                if role:
                    role_list.append(role)

            return role_list
        except Exception as e:
            logger.exception(e)
            return None

    def create_super_admin(self):
        """创建超级管理员角色"""
        if self.get_super_admin():
            logger.warning('Create Error:  super admin role existed')
            return None
        role_data = ROLES.get(ROLE_CODE_HOSP_SUPER_ADMIN)
        return self.create_role(**role_data)

    def get_super_admin(self):
        """
        获取超级管理员角色
        :return:
        """
        role = self.filter(codename=ROLE_CODE_HOSP_SUPER_ADMIN)

        if not role:
            logger.warning('Error: super admin role not existed')
            return None
        return role


class UserRoleShipManager(BaseManager):

    def create_user_role_ship(self):
        pass


class SequenceManager(BaseManager):

    def get_next_value(self, seq_code):
        seq = self.filter(seq_code=seq_code).first()
        if not seq:
            return None
        return seq.seq_value + 1

    def get_curr_value(self, seq_code):
        seq = self.filter(seq_code=seq_code).first()
        if not seq:
            return None
        return seq.seq_value


class HospitalAddressManager(BaseManager):

    def get_hospital_address_list(self):
        """
        获取医疗机构下资产设备存放地点列表（返回room级别的存放地点）
        """
        try:
            return self.exclude(parent=None, )
        except Exception as e:
            logger.exception(e)
            return None

    def get_storage_places(self):
        """
        获取医疗机构下资产设备存放地点列表

        """
        try:
            return self.filter(is_storage_place=True)
        except Exception as e:
            logger.exception(e)
            return None

    def get_storage_place_by_id(self, id):
        """
        获取医疗机构下资产设备存放地点列表

        """
        try:
            return self.filter(id=id, is_storage_place=True)
        except Exception as e:
            logger.exception(e)
            return None

    def get_hospital_address_by_ids(self, ids):
        """
        通过存储地点ID集合查询存储地点
        :param ids: 资产设备存储地点list
        """
        try:
            return self.filter(id__in=ids)
        except Exception as e:
            logger.exception(e)
            return None

    def create_storage_place(self, storage_places):
        """
        批量创建资产设备存储地点
        :return:
        """
        try:
            storage_place_list = []
            for sp in storage_places:
                storage_place_list.append(self.model(**sp))

            return self.bulk_create(storage_place_list)

        except Exception as e:
            logger.exception(e)
            return None

    def create_address(self, operator, hospital, title, is_storage_place, parent, *args, **kwargs):
        """
        创建存储地址信息
        默认parent=None时，为根节点地址，即parent=None的地址仅能有一条记录
        :param operator:
        :param hospital:
        :param title:
        :param is_storage_place:
        :param parent:
        :param args:
        :param kwargs:
        :return:
        """

        root_address_qs = self.filter(parent=None)
        if not root_address_qs and parent:
            return False, '未设置归属医院，请联系管理员'
        if root_address_qs and not parent:
            return False, '归属医院已存在'
        data = {
            'title': title,
            'is_storage_place': is_storage_place,
            'parent': parent
        }
        if kwargs.get('desc') is not None:
            data['desc'] = kwargs.get('desc')
        data['creator'] = operator
        data['hospital'] = hospital

        if is_storage_place:
            data['dept'] = kwargs.get('dept')
        siblings = self.filter(parent=parent)
        if not siblings:
            data['sort'] = 1
        else:
            max_sort_address = siblings.order_by('-sort')[::][0]
            data['sort'] = max_sort_address.sort + 1
        if not parent:
            data['level'] = 1
            # 相同分支，相同层级的title不能重复
            if self.filter(title=title, parent=parent):
                return False, '已存在相同名称的地址'
        else:
            # # 父节点为存储地址时，不能在添加子节点
            if parent.is_storage_place:
                return False, '数据异常'
            data['level'] = parent.level + 1
            if self.filter(title=title, parent=parent):
                return False, '已存在相同名称的地址'
            if parent.parent_path:
                data['parent_path'] = '-'.join([parent.parent_path, str(parent.id)])
            else:
                data['parent_path'] = '-'.join([str(parent.id)])
        try:
            address, success = self.update_or_create(**data)
            return True, address
        except Exception as e:
            logger.exception(e)
            return False, "操作失败"

    def update_address(self, address, *args, **kwargs):
        if not isinstance(address, self.model):
            return None
        try:
            address.save()
            address.clear_cache()
            return address
        except Exception as e:
            logger.exception(e)
            return None

    def get_children(self, address):
        try:
            return self.filter(parent=address)
        except Exception as e:
            logger.exception(e)
            return None

    def get_tree(self):
        all_addresses = self.annotate(dept_name=F('dept__name')).values(
            'id', 'title', 'is_storage_place', 'parent_id', 'level', 'sort', 'disabled',
            'dept_id', 'dept_name', 'desc', 'hospital_id'
        )
        if not all_addresses:
            return None

        parent_ids = set()
        root_address = None
        for address in all_addresses:
            parent_ids.add(address.get('parent_id'))
            if not address.get('parent_id'):
                root_address = address
        if not root_address:
            logger.warning('root address not been set')
            return None

        parents = []
        for address in all_addresses:
            if address.get('id') in parent_ids:
                parents.append(address)
                address['has_children'] = True
            else:
                address['has_children'] = False

        self.gen_tree(root_address, all_addresses)
        return root_address

    def gen_tree(self, parent, addresses):
        if not parent:
            return None
        if not parent.get('has_children'):
            parent['children'] = []
        else:
            children = []
            for item in addresses:
                if item.get('parent_id') == parent.get('id'):
                    children.append(item)
                    parent['children'] = children
            for child in children:
                self.gen_tree(child, addresses)


class SequenceManager(BaseManager):

    def init_default_sequences(self):
        seq_list = []
        try:
            for k in dict(SEQ_CODE_CHOICES).keys():
                seq = self.create(**SEQUENCES.get(k))
                if seq:
                    seq_list.append(seq)
            return seq_list
        except Exception as e:
            logger.exception(e)
            return None
