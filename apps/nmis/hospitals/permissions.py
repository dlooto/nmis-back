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
from nmis.hospitals.consts import ROLE_CODE_HOSP_SUPER_ADMIN, ROLE_CODE_NORMAL_STAFF, ROLE_CODE_PRO_DISPATCHER, \
    ROLE_CODE_HOSP_REPORT_ASSESS, ROLE_CODE_SYSTEM_SETTING_ADMIN
from nmis.hospitals.models import Hospital, Role

logger = logging.getLogger(__name__)


class IsSuperAdmin(BasePermission):
    """
    仅允许系统超级管理员访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsHospSuperAdmin(BasePermission):
    # 区别于系统超级管理员(系统超级管理员可访问系统大后台)
    message = u'仅医院超级管理员可操作'

    def has_permission(self, request, view):
        """
        View/接口级权限检查
        """
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查.
        :param obj:  None
        """
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_HOSP_SUPER_ADMIN).first()
        return request.user.has_role(role)


class HospGlobalReportAssessPermission(BasePermission):
    """
    医院全局报表查看权限
    """
    message = u'仅统计信息查看者可查看'

    def has_permission(self, request, view):
        """
        View/接口级权限检查
        """
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查.
        :param obj: None
        """
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_HOSP_REPORT_ASSESS).first()
        return request.user.has_role(role)


class SystemManagePermission(BasePermission):
    """
    系统设置管理权限
    """
    message = u'仅系统管理员可操作'

    def has_permission(self, request, view):
        """
        View/接口级权限检查
        """
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        对象级权限检查.
        :param obj: None
        """
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_SYSTEM_SETTING_ADMIN).first()
        return request.user.has_role(role)


class HospitalStaffPermission(BasePermission):
    """
    医院普通员工权限
    """

    message = u'仅允许登录的医院员工可操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ对象
        """
        # if not isinstance(obj, Hospital):
        #     return False
        # if not is_login(request):
        #     return False
        staff = request.user.get_profile()
        if not staff:
            return False
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_NORMAL_STAFF).first()
        return request.user.has_role(role)


class ProjectDispatcherPermission(BasePermission):
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
        # staff = request.user.get_profile()
        # if staff.is_admin_for_hospital(obj):
        #     return True
        # if not isinstance(obj, Hospital):
        #     return False
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_PRO_DISPATCHER)
        return request.user.has_role(role)


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


class IsReadOnly(BasePermission):
    """
    View-level permission to only allow Read operation
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
