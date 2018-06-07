# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging


from rest_framework import serializers

from base.serializers import BaseModelSerializer
from nmis.hospitals.models import Department, Hospital, Staff

logs = logging.getLogger(__name__)


class HospitalSerializer(BaseModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


class DepartmentSerializer(BaseModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class StaffSerializer(BaseModelSerializer):
    # group_name = serializers.CharField(source='group.name')
    # group_cate = serializers.CharField(source='group.cate')
    # is_admin = serializers.CharField(source='group.is_admin')

    group_name = serializers.SerializerMethodField('_get_group_name')
    group_cate = serializers.SerializerMethodField('_get_group_cate')
    is_admin = serializers.SerializerMethodField('_is_admin')

    class Meta:
        model = Staff
        fields = (
            'id', 'user', 'dept', 'name', 'title',
            'is_admin', 'organ',
            'group', 'group_name', 'group_cate',
            'contact', 'email', 'created_time',
        )

    def _get_group_name(self, obj):
        return '' if not obj.group else obj.group.name

    def _get_group_cate(self, obj):
        return '' if not obj.group else obj.group.cate

    def _is_admin(self, obj):
        return False if not obj.group else obj.group.is_admin


