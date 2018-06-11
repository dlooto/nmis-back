# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging
from django.db import transaction
from apps.users.managers import UserManager


from base.models import BaseManager

logs = logging.getLogger(__name__)


class HospitalManager(BaseManager):
    pass


class StaffManager(BaseManager):

    def create_staff(self, **data):
        try:
            with transaction.atomic():
                #创建用户,并获取用户id
                auth = ['username', data['username']]
                auth_obj = tuple(auth)
                password = data['password']
                user = UserManager.create_param_user(auth_obj, password)
                data['user_id'] = user.pk
                staff = self.model(**data)
                staff.save()

        except Exception as e:
            logging.exception(e)
            return None

        return staff


class GroupManager(BaseManager):

    def get_by_key(self, group_key, organ):
        return self.get(cate=group_key, organ=organ).first()

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group
