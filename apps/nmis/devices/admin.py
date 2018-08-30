# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from nmis.devices.models import OrderedDevice, SoftwareDevice

logs = logging.getLogger(__name__)


class OrderedDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'project', 'type_spec', 'num', 'measure', 'planned_price',
        'real_price', 'purpose',
    )


class SoftwareDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cate', 'purpose', 'producer',
    )


class ContractDevice(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'contract', 'supplier'
        'real_price', 'num', 'real_total_amount',
        'purpose', 'producer'
        'type_spec', 'measure', 'planned_price',
    )


admin.site.register(OrderedDevice, OrderedDeviceAdmin)
admin.site.register(SoftwareDevice, SoftwareDeviceAdmin)
