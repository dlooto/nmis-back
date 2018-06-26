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

from base.common.permissions import is_login

logs = logging.getLogger(__name__)


class ProjectPerformerPermission(BasePermission):
    """
    项目负责人权限
    """
    message = '仅允许项目负责人进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        :param obj: 为project object
        """
        staff = request.user.get_profile()
        return obj.performer == staff if staff else False


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

