# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""
配合DRF框架Permission规范, 定义API接口访问控制权限
"""

import logging
import urllib

from rest_framework.permissions import BasePermission, SAFE_METHODS

from restfw_composed_permissions.base import (BaseComposedPermission, And, Or,
                                              BasePermissionComponent)
from restfw_composed_permissions.generic.components import (
    AllowAll, AllowOnlyAuthenticated, AllowOnlySafeHttpMethod,
    ObjectAttrEqualToObjectAttr)

from base.common.permissions import is_login

logs = logging.getLogger(__name__)


class IsSuperAdmin(BasePermission):
    """
    仅允许系统超级管理员访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsHospitalAdmin(BasePermission):

    message = u'仅医院管理员可操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ object
        """
        if not request.user.get_profile():
            return False

        return request.user.get_profile().is_admin_for_organ(obj)


class HospitalStaffPermission(BasePermission):
    """
    医院普通员工权限
    """

    message = u'仅允许登录的医院员工可操作'

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ对象
        """
        if not is_login(request):
            return False
        staff = request.user.get_profile()
        return staff.organ == obj if staff else False


class ProjectApproverPermission(BasePermission):
    """
    项目分配者权限对象
    """

    message = u'仅允许项目分配者进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ对象
        """
        staff = request.user.get_profile()
        if staff.is_admin_for_organ(obj):
            return True
        return staff.organ == obj and staff.has_project_approver_perm()


class ProjectCreatorPermission(BasePermission):
    """
    项目申请提交者权限
    """
    message = '仅允许项目申请提交者进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        :param obj: 为project object
        """
        staff = request.user.get_profile()
        return obj.creator == staff if staff else False


# class ProjectAdminPermission(BaseComposedPermission):
#     """
#     医院项目管理者权限
#
#     Example:
#         ```
#         def global_permission_set(self):
#             return Or(AllowOnlyAuthenticated, And(AllowAll, AllowOnlySafeHttpMethod))
#
#         def object_permission_set(self):
#             return AllowAll
#         ```
#     """
#     message = '仅允许项目管理者操作'
#
#     def global_permission_set(self):
#         return AllowOnlyAuthenticated
#
#     def object_permission_set(self):
#         return Or(IsHospitalAdmin, ProjectApproverPermission)


class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        # Instance must have an attribute named `owner`.
        return obj == request.user.get_profile()
