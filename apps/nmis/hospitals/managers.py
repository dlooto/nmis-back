# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging
from django.db import transaction


from users.models import User

from base.models import BaseManager

logs = logging.getLogger(__name__)


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
                    ('username', user_data.get('username')), user_data.get('password'), is_active=True,
                )
                return self.create(organ=organ, dept=dept, user=user, **data)
        except Exception as e:
            logging.exception(e)
            return None

    def batch_upload_staff(self, staff_data):
        # TODO: 暂时用如下方式进行批量添加员工信息，后续创建批量添加接口进行优化
        try:
            with transaction.atomic():
                for i in range(len(staff_data)):
                    user = User.objects.create_param_user(
                        ('username', staff_data[i].get('username')), password='111111', is_active=True,
                    )
                    staff = self.create(
                        organ=staff_data[i].get('organ'),
                        dept=staff_data[i].get('dept'),
                        user=user,
                        name=staff_data[i].get('staff_name'),
                        contact=staff_data[i].get('contact_phone'),
                        email=staff_data[i].get('email')
                    )
            return True
        except Exception as e:
            logging.exception(e)
            return False

    def get_staffs_by_name(self, organ, staff_name):
        """
        通过名字模糊查询返回员工列表
        :param staff_name: 员工姓名
        :return:
        """
        return self.filter(organ=organ, name__contains=staff_name)


class GroupManager(BaseManager):

    def get_by_key(self, group_key, organ):
        return self.get(cate=group_key, organ=organ).first()

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group
