# coding=utf-8
#
# Created by junn, on 2018/6/7
#

#

import logging


from rest_framework import serializers

from base.serializers import BaseModelSerializer
from nmis.hospitals.models import Department, Hospital, Staff, Group

logs = logging.getLogger(__name__)


class HospitalSerializer(BaseModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


class DepartmentSerializer(BaseModelSerializer):

    organ_name = serializers.SerializerMethodField('_get_organ_name')

    class Meta:
        model = Department
        fields = ('id', 'created_time', 'name', 'contact', 'desc', 'attri', 'organ_id',
                  'organ_name')

    def _get_organ_name(self, obj):
        return '' if not obj.organ else obj.organ.organ_name


class DepartmentStaffsCountSerializer(BaseModelSerializer):
    """
    返回科室对象中含员工数量
    """
    staffs_count = serializers.SerializerMethodField('_get_staff_count')

    class Meta:
        model = Department
        fields = ('id', 'created_time', 'name', 'contact', 'desc', 'attri', 'organ_id',
                  'staffs_count')

    def _get_staff_count(self, obj):
        return Staff.objects.get_count_by_dept(obj.organ, obj)


class StaffSerializer(BaseModelSerializer):

    organ_name = serializers.SerializerMethodField('_get_organ_name')
    dept_name = serializers.SerializerMethodField('_get_dept_name')
    staff_name = serializers.CharField(source='name')
    staff_title = serializers.CharField(source='title')
    username = serializers.SerializerMethodField('_get_user_username')
    is_admin = serializers.SerializerMethodField('_is_admin')
    group_name = serializers.SerializerMethodField('_get_group_name')
    group_cate = serializers.SerializerMethodField('_get_group_cate')
    contact_phone = serializers.CharField(source='contact')

    class Meta:
        model = Staff
        fields = (
            'id', 'organ_id', 'organ_name',
            'dept_id', 'dept_name',
            'staff_name', 'staff_title',
            'user_id', 'username', 'is_admin',
            'group_id', 'group_name', 'group_cate',
            'contact_phone', 'email', 'created_time',
        )

    def _get_group_name(self, obj):
        return '' if not obj.group else obj.group.name

    def _get_group_cate(self, obj):
        return '' if not obj.group else obj.group.cate

    def _is_admin(self, obj):
        return False if not obj.group else obj.group.is_admin

    def _get_user_username(self, obj):
        return '' if not obj.user else obj.user.username

    def _get_organ_name(self, obj):
        return '' if not obj.organ else obj.organ.organ_name

    def _get_dept_name(self, obj):
        return '' if not obj.dept else obj.dept.name


class GroupSerializer(BaseModelSerializer):

    organ_name = serializers.SerializerMethodField('_get_organ_name')

    class Meta:
        model = Group
        fields = ('id', 'created_time', 'name', 'is_admin', 'desc', 'cate', 'organ_id',
                  'organ_name', 'permissions')

    def _get_organ_name(self, obj):
        return '' if not obj.organ else obj.organ.organ_name
