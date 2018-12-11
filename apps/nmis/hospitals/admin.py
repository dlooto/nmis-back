# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from nmis.hospitals.models import Role, UserRoleShip, HospitalAddress, Sequence
from .models import Hospital, Staff, Department

logger = logging.getLogger(__name__)


class HospitalAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'organ_name', 'industry', 'address', 'contact', 'auth_status', 'creator',
        'created_time', 'parent', 'grade'
    )
    list_display_links = ('id', 'organ_name')
    search_fields = ('id', 'organ_name')


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'attri', 'organ', 'created_time')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')


class StaffAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'organ', 'dept', 'title', 'contact')
    list_display_links = ('id', 'name', )
    list_filter = ('dept__name', )
    search_fields = ('id', 'name', 'contact', 'title', 'email', 'organ__organ_name')

    def save_model(self, request, obj, form, change):
        super(StaffAdmin, self).save_model(request, obj, form, change)
        obj.clear_cache()


class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'codename', 'desc')
    list_display_links = ('id', 'name', 'codename')
    search_fields = ('name', 'codename', 'desc')


class UserRoleShipAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', )
    list_display_links = ('id', 'user', 'role',)
    search_fields = ('id', 'user', 'role',)


class HospitalAddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'is_storage_place', 'parent', 'level', 'sort', 'disabled', 'dept')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', 'is_storage_place')


class SequenceAdmin(admin.ModelAdmin):
    list_display = ('id', 'seq_code', 'seq_name', 'seq_value', 'increment', 'remark')
    list_display_links = ('id', 'seq_code', 'seq_name')
    search_fields = ('id', 'seq_code', 'seq_name')


admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(UserRoleShip, UserRoleShipAdmin)
admin.site.register(HospitalAddress, HospitalAddressAdmin)
admin.site.register(Sequence, SequenceAdmin)

from django.contrib.auth.models import Group as _Group
from django.contrib.sites.models import Site as _Site

admin.site.unregister((_Group, _Site))
