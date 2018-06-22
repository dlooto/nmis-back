# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging


from rest_framework import serializers

from base.serializers import BaseModelSerializer
from .models import OrderedDevice

logs = logging.getLogger(__name__)


class OrderedDeviceSerializer(BaseModelSerializer):
    class Meta:
        model = OrderedDevice
        fields = (
            'id', 'name', 'cate', 'type_spec', 'purpose', 'project_id',
            'measure', 'num', 'planned_price', 'real_price', 'created_time',
        )

