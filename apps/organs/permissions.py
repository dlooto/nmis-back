# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""
配合DRF框架Permission规范, 定义API接口访问控制权限
"""

import logging
import urllib

from rest_framework.permissions import BasePermission, SAFE_METHODS

from base.common.permissions import is_login

logs = logging.getLogger(__name__)


class IsSuperAdmin(BasePermission):
    """
    仅允许系统超级管理员访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsOrganAdmin(BasePermission):

    message = u'仅企业管理员可操作'

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ object
        """
        if not is_login(request):
            return False
        return request.user.get_profile().is_admin_for_organ(obj)


class OrganStaffPermission(BasePermission):
    """
    仅允许登录的企业员工操作
    """
    message = u'仅允许登录的企业员工操作'

    def has_object_permission(self, request, view, obj):
        """
        :param obj: organ object
        """
        if not is_login(request):
            return False
        staff = request.user.get_profile()
        if staff.is_admin_for_organ(obj):
            return True
        return staff.organ == obj


class UnloginStaffPermission(BasePermission):
    """
    企业未登录员工权限: 作为未登录员工, 以_k进行鉴权处理
    """
    from .models import StaffSecureRecord

    k = '_k'
    k_class = StaffSecureRecord

    def has_object_permission(self, request, view, obj):
        hash_key = self.get_hash_key(request)
        secure_record = self.k_class.objects.filter(key=hash_key).first()
        if secure_record and secure_record.is_valid():
            staff = secure_record.user.get_profile()
            return self.check_staff(staff, obj)
        return False

    def check_staff(self, staff, obj):
        return staff.is_st_or_in_group() and obj == staff.organ

    def get_hash_key(self, request):
        # return request.data.get(self.k, '') or request.GET.get(self.k, '')
        return urllib.unquote(request.data.get(self.k, '')) or \
               urllib.unquote(request.GET.get(self.k, ''))


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