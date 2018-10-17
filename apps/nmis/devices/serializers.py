# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from rest_framework import serializers

from base.serializers import BaseModelSerializer
from .models import OrderedDevice, SoftwareDevice, ContractDevice, AssertDevice, \
    MedicalDeviceSix8Cate
from nmis.devices.models import RepairOrder
from nmis.hospitals.serializers import StaffSerializer


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


class RepairOrderSerializer(BaseModelSerializer):
    applicant_name = serializers.SerializerMethodField('_get_applicant_name')
    applicant_dept_name = serializers.SerializerMethodField('_get_applicant_dept_name')
    applicant_contact = serializers.SerializerMethodField('_get_applicant_contact')
    fault_type_title = serializers.SerializerMethodField('_get_fault_type_title')
    maintainer_name = serializers.SerializerMethodField('_get_maintainer_name')
    maintainer_contact = serializers.SerializerMethodField('_get_maintainer_contact')

    creator_name = serializers.SerializerMethodField('_get_creator_name')
    modifier_name = serializers.SerializerMethodField('_get_modifier_name')

    class Meta:
        model = RepairOrder
        fields = (
            'order_no', 'applicant_id', 'applicant_name', 'applicant_dept_name', 'applicant_contact',
            'fault_type_id', 'fault_type_title', 'desc', 'maintainer_id', 'maintainer_name', 'maintainer_contact',
            'expenses', 'result', 'solution', 'doc_list', 'priority', 'status',
            'comment_grade','comment_content', 'comment_time',
            'creator_id', 'creator_name', 'modifier_id', 'modifier_name', 'modified_time'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('fault_type', 'applicant', 'maintainer', 'creator', 'modifier')
        return queryset

    def _get_applicant_name(self, obj):
        return obj.applicant.name if obj.applicant else ''

    def _get_applicant_dept_name(self, obj):
        return obj.applicant.dept.name if obj.applicant and obj.applicant.dept else ''

    def _get_applicant_contact(self, obj):
        return obj.applicant.contact if obj.applicant else ''

    def _get_fault_type_title(self, obj):
        return obj.fault_type.title if obj.fault_type else ''

    def _get_maintainer_name(self, obj):
        return obj.maintainer.name if obj.maintainer else ''

    def _get_maintainer_contact(self, obj):
        return obj.maintainer.contact if obj.maintainer else ''

    def _get_creator_name(self, obj):
        return obj.creator.name if obj.creator else ''

    def _get_modifier_name(self, obj):
        return obj.modifier.name if obj.modifier else ''

