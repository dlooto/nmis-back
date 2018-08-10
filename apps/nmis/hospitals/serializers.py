# coding=utf-8
#
# Created by junn, on 2018/6/7
#

#

import logging

from django.db.models import Prefetch
from rest_framework import serializers

from base import resp
from base.serializers import BaseModelSerializer
from nmis.hospitals.models import Department, Hospital, Staff, Group, Role, UserRoleShip

logs = logging.getLogger(__name__)


class HospitalSerializer(BaseModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):

    organ_name = serializers.SerializerMethodField('_get_organ_name')

    @staticmethod
    def setup_eager_loading(query_set):
        query_set = query_set.select_related('organ')
        return query_set

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

    @staticmethod
    def setup_eager_loading(query_set):
        query_set = query_set.select_related('organ')
        query_set = query_set.prefetch_related('staff_set')
        return query_set

    class Meta:
        model = Department
        fields = ('id', 'created_time', 'name', 'contact', 'desc', 'attri', 'organ_id',
                  'staffs_count')

    def _get_staff_count(self, obj):
        return obj.staff_set.all().count()


class SimpleDepartmentSerializer(BaseModelSerializer):
    """
    返回科室对象,只包含id和name
    """
    class Meta:
        model = Department
        fields = ('id',  'name')


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
    # roles = serializers.SerializerMethodField('_get_user_roles')

    class Meta:
        model = Staff
        fields = (
            'id', 'organ_id', 'organ_name',
            'dept_id', 'dept_name',
            'staff_name', 'staff_title',
            'user_id', 'username', 'is_admin',
            'group_id', 'group_name', 'group_cate',
            'contact_phone', 'email', 'created_time', # 'roles'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('organ', 'dept', 'user', 'group')
        return queryset

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

    # def _get_user_roles(self, obj):
    #     """
    #     TODO: 待优化：应用
    #     :param obj:
    #     :return:
    #     """
    #     roles = obj.user.roles.prefetch_related().all()
    #     for role in roles:
    #         dept_domains = role.get_user_role_dept_domains(obj.user)
    #         setattr(role, 'dept_domains', dept_domains)
    #     # roles = RoleSerializer.setup_eager_loading(roles)
    #     return resp.serialize_data(roles, srl_cls_name='RoleSerializer')


class UserRoleShipSerializer(BaseModelSerializer):
    role_name = serializers.SerializerMethodField('_get_role_name')
    role_codename = serializers.SerializerMethodField('_get_role_codename')
    role_permissions = serializers.SerializerMethodField('_get_role_permissions')
    dept_domains = SimpleDepartmentSerializer(many=True, read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('role', 'user', )
        queryset = queryset.prefetch_related('dept_domains', 'role__permissions')
        return queryset

    class Meta:
        model = UserRoleShip
        fields = (
            'role_id', 'role_name', 'role_codename', 'role_permissions',
            'dept_domains',
        )

    def _get_role_name(self, obj):
        return obj.role.name if obj.role else ''

    def _get_role_codename(self, obj):
        return obj.role.codename if obj.role else ''

    def _get_role_permissions(self, obj):
        if not obj.role:
            return []
        return resp.serialize_data(
            obj.role.permissions.all(), srl_cls_name='SimplePermissionSerializer'
        )


class StaffWithRoleSerializer(StaffSerializer):

    user_role_ships = serializers.SerializerMethodField('_get_user_role_ships')
    #user__user_role_ships = UserRoleShipSerializer(many=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related(
            'organ', 'dept', 'group', 'user',
            'user__user_role_ships'
            'user__user_role_ships__role'
            'user__user_role_ships__role__dept_domains'
        )
        # queryset = queryset.prefetch_related(
        #     'user__user_role_ships'
        #     'user__user_role_ships__role'
        #     'user__user_role_ships__role__dept_domains'
        # )
        queryset = queryset.prefetch_related(
            Prefetch(
                'user__user_role_ships',
                queryset=queryset.prefetch_related('user__user_role_ships')
            )
        )
        return queryset

    class Meta:
        model = Staff
        fields = (
            'id', 'organ_id', 'organ_name',
            'dept_id', 'dept_name',
            'staff_name', 'staff_title',
            'user_id', 'username', 'is_admin',
            'group_id', 'group_name', 'group_cate',
            'contact_phone', 'email', 'created_time',
            'user_role_ships',
        )

    def _get_user_role_ships(self, obj):
        """
        :param obj:
        :return:
        """
        user_role_ships = UserRoleShip.objects.filter(user__in=[obj.user])
        #user_role_ships = obj.user.user_role_ships.all()
        user_role_ships = UserRoleShipSerializer.setup_eager_loading(user_role_ships)
        return resp.serialize_data(user_role_ships, srl_cls_name='UserRoleShipSerializer')


class SimpleStaffSerializer(BaseModelSerializer):

    organ_name = serializers.SerializerMethodField('_get_organ_name')
    dept_name = serializers.SerializerMethodField('_get_dept_name')
    staff_name = serializers.CharField(source='name')
    staff_title = serializers.CharField(source='title')
    username = serializers.SerializerMethodField('_get_user_username')
    is_admin = serializers.SerializerMethodField('_is_admin')
    group_name = serializers.SerializerMethodField('_get_group_name')
    group_cate = serializers.SerializerMethodField('_get_group_cate')
    contact_phone = serializers.CharField(source='contact')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('organ', 'dept', 'user', 'group')
        return queryset

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

    @staticmethod
    def set_eager_loading(queryset):
        queryset = queryset.select_related('organ')
        return queryset

    class Meta:
        model = Group
        fields = ('id', 'created_time', 'name', 'is_admin', 'desc', 'cate', 'organ_id',
                  'organ_name',)

    def _get_organ_name(self, obj):
        return '' if not obj.organ else obj.organ.organ_name


class PermissionSerializer(BaseModelSerializer):
    """
    权限序列化类.
    TODO:暂时把group当做permission处理，后续改造为真正的Permission,要去掉is_admin
    """
    codename = serializers.SerializerMethodField('_get_codename')

    @staticmethod
    def set_eager_loading(queryset):
        queryset = queryset.select_related('organ')
        return queryset

    class Meta:
        model = Group
        fields = ('id', 'name', 'codename', 'desc',  'created_time')

    def _get_codename(self, obj):
        return obj.cate


class SimplePermissionSerializer(BaseModelSerializer):
    """
    权限序列化类.
    TODO:暂时把group当做permission处理，后续改造为真正的Permission,要去掉is_admin
    """
    codename = serializers.SerializerMethodField('_get_codename')

    class Meta:
        model = Group
        fields = ('id', 'name', 'codename')

    def _get_codename(self, obj):
        return obj.cate


class ChunkRoleSerializer(BaseModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    @staticmethod
    def set_eager_loading(queryset):
        queryset = queryset.prefetch_related('permissions')
        return queryset

    class Meta:
        model = Role
        fields = ('id', 'name', 'codename',  'desc', 'permissions', 'created_time')


class RoleSerializer(BaseModelSerializer):
    permissions = SimplePermissionSerializer(many=True, read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related(
            'permissions',
        )
        return queryset

    class Meta:
        model = Role
        fields = ('id', 'name', 'codename', 'desc', 'permissions',
                  'created_time')


class SimpleRoleSerializer(BaseModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name', 'codename')



