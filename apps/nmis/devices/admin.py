# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from nmis.devices.models import OrderedDevice, SoftwareDevice, ContractDevice, MedicalDeviceSix8Cate, AssertDevice, \
    AssertDeviceRecord, FaultType, RepairOrder, RepairOrderRecord, MaintenancePlan, FaultSolution

logger = logging.getLogger(__name__)


class OrderedDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'project', 'type_spec', 'num', 'measure', 'planned_price',
        'real_price', 'purpose',
    )


class SoftwareDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cate', 'purpose', 'producer',
    )


class ContractDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'contract', 'supplier',
        'real_price', 'num', 'real_total_amount',
        'purpose', 'producer',
        'type_spec', 'measure', 'planned_price',
    )


class MedicalDeviceSix8CateAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'code', 'title', 'parent', 'mgt_cate', 'level',
    )
    search_fields = ()
    list_display_links = ()


class AssertDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'assert_no', 'title', 'cate', 'medical_device_cate',
        'use_dept', 'responsible_dept', 'storage_place',  'status', 'state',
    )


class AssertDeviceRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'assert_device', 'operation', 'msg_content', 'reason'

    )
    search_fields = ()
    list_display_links = ()


class FaultTypeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'parent', 'level', 'sort',
    )
    search_fields = ()
    list_display_links = ()


class RepairOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'applicant', 'fault_type', 'maintainer',
        'priority', 'status',
    )
    search_fields = ()
    list_display_links = ()


class RepairOrderRecordAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'repair_order', 'operation', 'msg_content', 'reason'

    )
    search_fields = ()
    list_display_links = ()


class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'type', 'start_date', 'expired_date',
        'status', 'period_measure', 'period_num',
    )
    search_fields = ()
    list_display_links = ()


class FaultSolutionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'fault_type', 'status', 'modified_time'
    )
    search_fields = ()
    list_display_links = ()


admin.site.register(OrderedDevice, OrderedDeviceAdmin)
admin.site.register(SoftwareDevice, SoftwareDeviceAdmin)
admin.site.register(ContractDevice, ContractDeviceAdmin)
admin.site.register(MedicalDeviceSix8Cate, MedicalDeviceSix8CateAdmin)
admin.site.register(AssertDevice, AssertDeviceAdmin)
admin.site.register(AssertDeviceRecord, AssertDeviceRecordAdmin)
admin.site.register(FaultType, FaultTypeAdmin)
admin.site.register(RepairOrder, RepairOrderAdmin)
admin.site.register(RepairOrderRecord, RepairOrderRecordAdmin)
admin.site.register(MaintenancePlan, MaintenancePlanAdmin)
admin.site.register(FaultSolution, FaultSolutionAdmin)




