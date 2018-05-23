# coding=utf-8
#
# Created by junn, on 16/12/25
#

"""

"""

import logging

from rest_framework.permissions import BasePermission

logs = logging.getLogger(__name__)


class IsSuperAdmin(BasePermission):
    """
    仅允许系统超级管理员访问
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class BlacklistPermission(BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    # def has_permission(self, request, view):
    #     ip_addr = request.META['REMOTE_ADDR']
    #     blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
    #     return not blacklisted

    pass