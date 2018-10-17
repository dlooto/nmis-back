# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from base.serializers import BaseModelSerializer
from .models import OrderedDevice, SoftwareDevice, ContractDevice, AssertDevice, \
    MedicalDeviceSix8Cate

logger = logging.getLogger(__name__)


class OrderedDeviceSerializer(BaseModelSerializer):
    class Meta:
        model = OrderedDevice
        fields = (
            'id', 'name', 'cate', 'type_spec', 'purpose', 'project_id',
            'measure', 'num', 'planned_price', 'real_price', 'created_time',
        )

    @staticmethod
    def setup_eager_loading(queryset):
        pass


class SoftwareDeviceSerializer(BaseModelSerializer):
    class Meta:
        model = SoftwareDevice
        fields = (
            'id', 'name', 'cate', 'purpose', 'producer', 'created_time', 'planned_price'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        pass


class ContractDeviceSerializer(BaseModelSerializer):

    class Meta:
        model = ContractDevice
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        pass


class AssertDeviceSerializer(BaseModelSerializer):
    class Meta:
        model = AssertDevice
        fields = '__all__'

    @staticmethod
    def setup_eager_loading(queryset):
        pass


class MedicalDeviceSix8CateSerializer(BaseModelSerializer):
    class Meta:
        model = MedicalDeviceSix8Cate
        fields = ('id', 'title')

    @staticmethod
    def setup_eager_loading(queryset):
        pass
