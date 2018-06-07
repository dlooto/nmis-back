# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging

from base.models import BaseManager

logs = logging.getLogger(__name__)


class HospitalManager(BaseManager):
    pass


class StaffManager(BaseManager):
    pass


class GroupManager(BaseManager):

    def get_by_key(self, group_key, organ):
        return self.get(cate=group_key, organ=organ).first()

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group
