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
    pass


class StaffManager(BaseManager):

    def create_staff(self, organ, dept, user, **data):
        try:
            with transaction.atomic():
                # create User object first ...
                # TODO: 待模型修改后，去掉email参数
                user = User.objects.create_param_user(
                    ('username', user.get_username()), user.password, is_active=True,
                    email='zhangsan04@example.com'
                )
                user.set_password(user.password)
                return self.create(organ=organ, dept=dept, user=user, **data)
        except Exception as e:
            logging.exception(e)
            return None


class GroupManager(BaseManager):

    def get_by_key(self, group_key, organ):
        return self.get(cate=group_key, organ=organ).first()

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group
