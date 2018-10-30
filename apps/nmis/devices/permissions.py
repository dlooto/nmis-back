# coding=utf-8
#
# Created by gong, on 2018-10-16
#

# import logging
#
# from django.contrib.auth.models import Permission
# from rest_framework.permissions import BasePermission
#
# from base.common.permissions import is_login
# from nmis.devices.models import AssertDevice
#
# logger = logging.getLogger(__name__)
#
#
# class AssertDeviceAdminPermission(BasePermission):
#     """
#     项目分配者权限对象
#     """
#
#     message = u'仅允许项目分配者进行操作'
#
#     def has_permission(self, request, view):
#         if not is_login(request):
#             return False
#         staff = request.user.get_profile()
#         Permission.objects.filter(content_type__app_label=self.__module__, content_type__model=AssertDevice)
#        return True

