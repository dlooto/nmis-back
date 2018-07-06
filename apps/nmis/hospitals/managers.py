# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging
from django.db import transaction


from users.models import User

from base.models import BaseManager
from utils import times

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

    def batch_upload_staffs(self, staffs_data):
        try:
            with transaction.atomic():
                user_list = []
                for data in staffs_data:
                    user = User(
                        username=data.get('username'), password='111111',
                        is_active=True, is_staff=False, is_superuser=False,
                        last_login=times.now(), date_joined=times.now()
                    )
                    user.set_password('111111')
                    user_list.append(user)
                none_id_users = User.objects.bulk_create(user_list)

                users = User.objects.filter(username__in=[user.username for user in none_id_users])

                user_dict = {}
                for user in users:
                    user_dict[user.username] = user

                staff_list = []
                for data in staffs_data:
                    staff_list.append(
                        self.model(
                            organ=data.get('organ'), dept=data.get('dept'),
                            user=user_dict[data.get('username')],
                            name=data.get('staff_name'),
                            contact=data.get('contact_phone'),
                            email=data.get('email')
                    ))
                self.bulk_create(staff_list)
            return True
        except Exception as e:
            logging.exception(e)
            return False

    def get_by_name(self, organ, staff_name):
        """
        通过名字模糊查询返回员工列表
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


class GroupManager(BaseManager):

    def get_by_key(self, group_key, organ):
        return self.get(cate=group_key, organ=organ).first()

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group
