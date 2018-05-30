# coding=utf-8
#
# Created by Junn, on 2018-5-29
# 
#

import logging

from django.core.cache import cache
from base.models import BaseManager

logs = logging.getLogger(__name__)


class PermissionManager(BaseManager):
    use_in_migrations = True

    def get_by_key(self, codename):
        return self.get(codename=codename)

    def list_by_cate(self, cate):
        """ 按类别返回权限集合 """
        return self.filter(cate=cate)

    def get_all(self):
        return self.all()


class GroupManager(BaseManager):
    """
    The manager for the auth's Group model.
    """
    use_in_migrations = True

    def get_by_key(self, name):
        return self.get(name=name)

    def create_group(self, organ, commit=True, **kwargs):
        group = self.model(organ=organ, **kwargs)
        if commit:
            group.save()
        return group


class OrganManager(BaseManager):

    def create_organ(self, **kwargs):
        organ = self.model(**kwargs)
        organ.save()

        return organ

    # def create_staff(self, **kwargs):
    #     from .models import Staff
    #     staff = Staff(**kwargs)
    #     staff.save()
    #     return staff
    #
    # def create_department(self, **kwargs):
    #     from .models import Department
    #     department = Department(**kwargs)
    #     department.save()
    #     return department


class StaffManager(BaseManager):

    def custom_filter(self, *args, **kwargs):
        kwargs['status'] = self.model.NORMAL_STATUS
        return super(StaffManager, self).filter(*args, **kwargs)

    def filter_obj(self, obj):
        if obj and obj.status != self.model.NORMAL_STATUS:
            return None
        return obj

    def get_by_id(self, obj_id):
        obj = super(StaffManager, self).get_by_id(obj_id)
        return self.filter_obj(obj)

    def get_cached(self, obj_id):
        obj = super(StaffManager, self).get_cached(obj_id)
        return self.filter_obj(obj)

    def get_cached_many(self, obj_id_list):
        """
        返回缓存中的多个对象列表, 通过id列表
        :param obj_id_list:
        :return:
        """
        if not obj_id_list:
            return None

        objs = cache.get_many(obj_id_list)
        if not objs or len(objs) < len(obj_id_list):
            objs = self.custom_filter(id__in=obj_id_list)
            if not objs:
                return None
            for obj in objs:
                obj.cache()
        return objs


