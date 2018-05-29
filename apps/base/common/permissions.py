# coding=utf-8
#
# Created by junn, on 17/4/6
#

# 

import logging

from rest_framework.permissions import BasePermission

logs = logging.getLogger(__name__)


def is_login(request):
    return request.user and request.user.is_authenticated

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

    def __unicode__(self):
        return u'<OrPermission {0} initialed: {1}>'.format(self.perms, self.initialed)

    def __str__(self):
        return self.__unicode__().encode('utf-8')


class OrPermission(_Permission):
    operator = any


class AndPermission(_Permission):
    operator = all