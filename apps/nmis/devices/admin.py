# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin

from nmis.devices.models import OrderedDevice

logs = logging.getLogger(__name__)


class OrderedDeviceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'project', 'type_spec', 'num', 'measure', 'planned_price', 'real_price',
        'purpose',
    )

admin.site.register(OrderedDevice, OrderedDeviceAdmin)
