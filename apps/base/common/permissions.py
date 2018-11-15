# coding=utf-8
#
# Created by junn, on 17/4/6
#

# 

import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


def is_login(request):
    return request.user and request.user.is_authenticated


class CustomAllPermission(BasePermission):
    """
    自定义检查用户权限类
    """
    def has_permission(self, request, view):
        """
        View/接口级权限检查
        """
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, dict):
            return False
        permission_codes = ()
        if obj.get('permission_codes'):
            permission_codes = obj.get('permission_codes')

        permissions = request.user.get_permissions()

        code_names = []

        for permission in permissions:
            code_names.append(permission.cate)

        for code in permission_codes:
            if code not in code_names:
                return False
        return True


class CustomAnyPermission(BasePermission):
    """
    自定义检查用户权限类
    """

    def has_permission(self, request, view):
        """
        View/接口级权限检查
        """
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, dict):
            return False
        permission_codes = ()
        if obj.get('permission_codes'):
            permission_codes = obj.get('permission_codes')

        permissions = request.user.get_permissions()
        code_names = []

        for permission in permissions:
            code_names.append(permission.cate)

        for code in permission_codes:
            if code in code_names:
                return True
        return False


def check_organ_any_permissions(request, view):
    staff = request.user.get_profile() if hasattr(request.user, 'get_profile') else None
    view.check_object_any_permissions(request, getattr(staff, 'organ', None))
    return staff


class _Permission(BasePermission):
    operator = None

    def __init__(self, *perms):
        self.perms = perms
        self.initialed = False

    def __call__(self, *args, **kwargs):
        self.initialed = True
        return self

    def has_permission(self, request, view):
        return self.operator([permission_class().has_permission(request, view) for permission_class in self.perms])

    def has_object_permission(self, request, view, obj):
        return self.operator(
            [permission_class().has_object_permission(request, view, obj) for permission_class in self.perms]
        )

    def __unicode__(self):
        return u'<OrPermission {0} initialed: {1}>'.format(self.perms, self.initialed)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class OrPermission(_Permission):
    """
    权限"或"操作
    """
    operator = any


class AndPermission(_Permission):
    """
    权限"与"操作
    """
    operator = all