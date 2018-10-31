# coding=utf-8
#
# Created by gong, on 2018-10-16


import logging

from rest_framework.permissions import BasePermission

from base.common.permissions import is_login
from nmis.devices.models import RepairOrder, MaintenancePlan
from nmis.hospitals.consts import ROLE_CODE_PRO_DISPATCHER, ROLE_CODE_MAINTAINER, ROLE_CODE_REPAIR_ORDER_DISPATCHER, \
    ROLE_CODE_ASSERT_DEVICE_ADMIN
from nmis.hospitals.models import Role


logger = logging.getLogger(__name__)


class AssertDeviceAdminPermission(BasePermission):
    """
    资产设备管理权限
    """
    message = u'仅允许资产管理员进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        """
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_ASSERT_DEVICE_ADMIN)
        return request.user.has_role(role)


class RepairOrderCreatorPermission(BasePermission):
    """
    报修单创建人权限
    """
    message = '仅允许报修单提交人进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, repair_order):
        """
        """
        if not isinstance(repair_order, RepairOrder):
            return False
        staff = request.user.get_profile()
        return repair_order.creator == staff if staff else False


class RepairOrderDispatchPermission(BasePermission):
    """
    报修单分派权
    """
    message = u'仅允许维修任务分配人可进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):
        """
        """
        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_REPAIR_ORDER_DISPATCHER)
        return request.user.has_role(role)


class MaintenancePlanExecutePermission(BasePermission):
    """
    设备维护保养计划执行权限
    """
    message = '仅允许维护计划执行人进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, maintenance_plan):
        """
        """
        if not isinstance(maintenance_plan, MaintenancePlan):
            return False
        staff = request.user.get_profile()
        return maintenance_plan.executor == staff if staff else False


class RepairOrderHandlePermission(BasePermission):
    """
    报修单处理人权限
    """
    message = '仅允许维修工程师进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, repair_order):
        """
        """
        if not isinstance(repair_order, RepairOrder):
            return False
        staff = request.user.get_profile()
        return repair_order.maintainer == staff if staff else False


class KnowledgeManagePermission(BasePermission):
    """
    知识库管理权限
    """
    message = '仅允许维修工程师进行操作'

    def has_permission(self, request, view):
        return is_login(request)

    def has_object_permission(self, request, view, obj):

        role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_MAINTAINER)
        return request.user.has_role(role)


