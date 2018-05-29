# coding=utf-8
#
# Created on 2018-5-29, by Junn
#

from rest_framework import serializers

from base.serializers import BaseModelSerializer
from .models import Staff, Department, Permission, Group, Organ


class OrganSerializer(BaseModelSerializer):
    class Meta:
        model = Organ
        fields = '__all__'


class StaffSerializer(BaseModelSerializer):
    group_name = serializers.CharField(source='group.name')
    group_cate = serializers.CharField(source='group.cate')
    is_admin = serializers.CharField(source='group.is_admin')

    class Meta:
        model = Staff
        fields = (
            'id', 'user', 'dept', 'name', 'title', 'contact', 'email', 'created_time',
            'group', 'group_name', 'group_cate', 'is_admin'
        )


class DepartmentSerializer(BaseModelSerializer):

    class Meta:
        model = Department
        fields = '__all__'


class PermissionSerializer(BaseModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class GroupSerializer(BaseModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'
