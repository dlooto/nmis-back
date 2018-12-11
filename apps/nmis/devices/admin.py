# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from nmis.devices.models import OrderedDevice, SoftwareDevice, ContractDevice, MedicalDeviceCate, AssertDevice, \
    AssertDeviceRecord, FaultType, RepairOrder, RepairOrderRecord, MaintenancePlan, FaultSolution

logger = logging.getLogger(__name__)


class OrderedDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'project', 'type_spec', 'num', 'measure', 'planned_price',
        'real_price', 'purpose',
    )
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', )


class SoftwareDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cate', 'purpose', 'producer',
    )
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', )


class ContractDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'contract', 'supplier',
        'real_price', 'num', 'real_total_amount',
        'purpose', 'producer',
        'type_spec', 'measure', 'planned_price',
    )
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name', )


class MedicalDeviceCateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'code', 'level_code', 'parent', 'mgt_cate', 'level',
    )
    list_display_links = ('id', 'title', 'code')
    search_fields = ('id', 'title', 'code')
    list_filter = ('level', 'mgt_cate')


class AssertDeviceAdmin(admin.ModelAdmin):

    list_display = (
        'id', 'assert_no', 'title', 'cate', 'medical_device_cate',
        'use_dept', 'responsible_dept', 'storage_place',  'status', 'state',
    )
    list_display_links = ('id', 'title', 'assert_no')
    search_fields = ('id', 'title', 'assert_no')
    list_filter = ('cate', 'medical_device_cate__title', 'status', 'state')


class AssertDeviceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'assert_device', 'operation', 'msg_content', 'reason'

    )
    list_display_links = ('id', 'assert_device')
    search_fields = ('id', 'assert_device', )


class FaultTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'parent', 'level', 'sort',
    )
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', )


class RepairOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'order_no', 'applicant', 'fault_type', 'maintainer',
        'priority', 'status',
    )
    list_display_links = ('id', 'order_no')
    search_fields = ('id', 'order_no', )


class RepairOrderRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'repair_order', 'operation', 'msg_content', 'reason'

    )
    list_display_links = ('id', 'repair_order')
    search_fields = ('id', 'repair_order', )


class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'type', 'start_date', 'expired_date',
        'status', 'period_measure', 'period_num',
    )
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', )


class FaultSolutionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'fault_type', 'status', 'modified_time'
    )
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', )


admin.site.register(OrderedDevice, OrderedDeviceAdmin)
admin.site.register(SoftwareDevice, SoftwareDeviceAdmin)
admin.site.register(ContractDevice, ContractDeviceAdmin)
admin.site.register(MedicalDeviceCate, MedicalDeviceCateAdmin)
admin.site.register(AssertDevice, AssertDeviceAdmin)
admin.site.register(AssertDeviceRecord, AssertDeviceRecordAdmin)
admin.site.register(FaultType, FaultTypeAdmin)
admin.site.register(RepairOrder, RepairOrderAdmin)
admin.site.register(RepairOrderRecord, RepairOrderRecordAdmin)
admin.site.register(MaintenancePlan, MaintenancePlanAdmin)
admin.site.register(FaultSolution, FaultSolutionAdmin)




