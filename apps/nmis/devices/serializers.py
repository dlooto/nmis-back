# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from rest_framework import serializers

from base import resp
from base.serializers import BaseModelSerializer
from nmis.documents.models import File
from .models import OrderedDevice, SoftwareDevice, ContractDevice, AssertDevice, \
    MedicalDeviceCate, MaintenancePlan
from nmis.devices.models import RepairOrder, FaultType, FaultSolution, RepairOrderRecord
from nmis.hospitals.serializers import StaffSerializer, HospitalAddressSerializer


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

    performer_name = serializers.SerializerMethodField('_get_performer_name')
    medical_device_cate_title = serializers.SerializerMethodField('_get_medical_device_cate_title')
    responsible_dept_name = serializers.SerializerMethodField('_get_responsible_dept_name')
    use_dept_name = serializers.SerializerMethodField('_get_use_dept_name')
    storage_place_title = serializers.SerializerMethodField('_get_storage_place_title')
    creator_name = serializers.SerializerMethodField('_get_creator_name')
    modifier_name = serializers.SerializerMethodField('_get_modifier_name')

    class Meta:
        model = AssertDevice
        fields = ('id', 'created_time', 'creator_id', 'creator_name', 'assert_no', 'title',
                  'medical_device_cate_id', 'medical_device_cate_title', 'serial_no',
                  'modifier_id', 'modifier_name', 'type_spec', 'service_life',
                  'performer_id', 'performer_name', 'responsible_dept_id',
                  'responsible_dept_name', 'use_dept_id', 'use_dept_name',
                  'production_date', 'bar_code', 'status', 'storage_place_id',
                  'storage_place_title', 'purchase_date', 'producer', 'cate')

    @staticmethod
    def setup_eager_loading(queryset):

        return queryset.select_related(
            'use_dept', 'creator', 'responsible_dept', 'medical_device_cate', 'performer',
            'storage_place', 'modifier'
        )

    def _get_performer_name(self, obj):
        return obj.performer.name if obj.performer else ''

    def _get_medical_device_cate_title(self, obj):
        return obj.medical_device_cate.title if obj.medical_device_cate else ''

    def _get_responsible_dept_name(self, obj):
        return obj.responsible_dept.name if obj.responsible_dept else ''

    def _get_use_dept_name(self, obj):
        return obj.use_dept.name if obj.use_dept else ''

    def _get_storage_place_title(self, obj):
        return obj.storage_place.title if obj.storage_place else ''

    def _get_creator_name(self, obj):
        return obj.creator.name if obj.creator else ''

    def _get_modifier_name(self, obj):
        return obj.modifier.name if obj.modifier else ''


class AssertDeviceBriefSerializer(BaseModelSerializer):

    class Meta:
        model = AssertDevice
        fields = ('id', 'assert_no', 'title')

    @staticmethod
    def setup_eager_loading(queryset):
        pass


class MedicalDeviceCateCatalogSerializer(BaseModelSerializer):
    title_display = serializers.SerializerMethodField()

    class Meta:
        model = MedicalDeviceCate
        fields = ('id', 'title', 'code', 'title_display')

    def get_title_display(self, obj):
        return '{} {}'.format(obj.code, obj.title)


class MedicalDeviceSecondGradeCateSerializer(BaseModelSerializer):
    """二级产品分类简要信息"""
    title_display = serializers.SerializerMethodField()

    class Meta:
        model = MedicalDeviceCate
        fields = ('id', 'title', 'code', 'title_display')

    def get_title_display(self, obj):
        return '{} {}'.format(obj.code, obj.title)


class MedicalDeviceSecondGradeCateDetailSerializer(BaseModelSerializer):
    """二级产品分类详情"""

    first_grade_cate = serializers.SerializerMethodField()
    title_display = serializers.SerializerMethodField()
    mgt_cate_display = serializers.SerializerMethodField()

    class Meta:
        model = MedicalDeviceCate
        fields = (
            'id', 'title', 'code', 'title_display', 'desc', 'example',
            'purpose', 'mgt_cate_display', 'first_grade_cate'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('parent')

    def get_title_display(self, obj):
        return '{} {}'.format(obj.code, obj.title)

    def get_first_grade_cate(self, obj):
        return '{} {}'.format(obj.parent.level_code, obj.parent.title)if obj.parent and obj.parent.title else ''

    def get_mgt_cate_display(self, obj):
        return obj.get_mgt_cate_display()


class FaultTypeSerializer(BaseModelSerializer):

    class Meta:
        model = FaultType
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
    repair_devices = AssertDeviceBriefSerializer(many=True)
    files = serializers.SerializerMethodField('_get_files')
    creator_name = serializers.SerializerMethodField('_get_creator_name')
    modifier_name = serializers.SerializerMethodField('_get_modifier_name')

    class Meta:
        model = RepairOrder
        fields = (
            'id', 'order_no', 'applicant_id', 'applicant_name', 'applicant_dept_name', 'applicant_contact',
            'fault_type_id', 'fault_type_title', 'desc', 'maintainer_id', 'maintainer_name', 'maintainer_contact',
            'expenses', 'result', 'solution', 'files', 'priority', 'status', 'repair_devices',
            'comment_grade', 'comment_content', 'comment_time',
            'creator_id', 'creator_name', 'created_time', 'modifier_id', 'modifier_name', 'modified_time'
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

    def _get_files(self, obj):
        if not obj.files:
            return []
        file_ids_str = obj.files.split(',')
        file_ids = [int(id_str) for id_str in file_ids_str]
        file_list = File.objects.filter(id__in=file_ids).all()
        return resp.serialize_data(file_list, srl_cls_name='FileSerializer') if file_list else []


class RepairOrderRecordSerializer(BaseModelSerializer):
    order_no = serializers.SerializerMethodField('_get_order_no')
    operator_name = serializers.SerializerMethodField('_get_operator_name')
    operator_dept_name = serializers.SerializerMethodField('_get_operator_dept_name')
    receiver_name = serializers.SerializerMethodField('_get_receiver_name')
    receiver_dept_name = serializers.SerializerMethodField('_get_receiver_dept_name')

    class Meta:
        model = RepairOrderRecord
        fields = (
            'id', 'repair_order_id', 'order_no', 'operation', 'reason', 'operator_id', 'operator_name', 'operator_dept_name',
            'receiver_id', 'receiver_name', 'receiver_dept_name', 'msg_content', 'created_time'
        )

    def _get_order_no(self, obj):
        return obj.repair_order.order_no if obj.repair_order and obj.repair_order.order_no else ''

    def _get_operator_name(self, obj):
        return obj.operator.name if obj.operator else ''

    def _get_operator_dept_name(self, obj):
        return obj.operator.dept.name if obj.operator and obj.operator.dept else ''

    def _get_receiver_name(self, obj):
        return obj.receiver.name if obj.receiver else ''

    def _get_receiver_dept_name(self, obj):
        return obj.receiver.dept.name if obj.receiver and obj.receiver.dept else ''


class MaintenancePlanSerializer(BaseModelSerializer):

    assert_devices = AssertDeviceSerializer(many=True)
    storage_places = serializers.SerializerMethodField('_get_storage_places')
    executor_name = serializers.SerializerMethodField('_get_executor_name')
    creator_name = serializers.SerializerMethodField('_get_creator_name')
    modifier_name = serializers.SerializerMethodField('_get_modifier_name')

    class Meta:
        model = MaintenancePlan
        fields = ('id', 'plan_no', 'title', 'start_date', 'type', 'expired_date',
                  'executor_id', 'executor_name', 'creator_id', 'creator_name',
                  'modifier_id', 'modifier_name', 'modified_time', 'status',
                  'storage_places', 'assert_devices', 'result', 'executed_date')

    def _get_storage_places(self, obj):
        storage_places = obj.places.all()

        return resp.serialize_data(storage_places) if storage_places else []

    def _get_executor_name(self, obj):

        return obj.executor.name if obj.executor else ''

    def _get_creator_name(self, obj):

        return obj.creator.name if obj.creator else ''

    def _get_modifier_name(self, obj):

        return obj.modifier.name if obj.modifier else ''


class MaintenancePlanListSerializer(BaseModelSerializer):

    executor_name = serializers.SerializerMethodField('_get_executor_name')
    creator_name = serializers.SerializerMethodField('_get_creator_name')
    modifier_name = serializers.SerializerMethodField('_get_modifier_name')
    storage_places = serializers.SerializerMethodField('_get_storage_places')

    class Meta:
        model = MaintenancePlan
        fields = ('id', 'plan_no', 'title', 'start_date', 'type', 'expired_date',
                  'executor_id', 'executor_name', 'creator_id', 'creator_name',
                  'modifier_id', 'modifier_name', 'modified_time', 'status',
                  'result', 'executed_date', 'storage_places')

    def _get_executor_name(self, obj):

        return obj.executor.name if obj.executor else ''

    def _get_creator_name(self, obj):

        return obj.creator.name if obj.creator else ''

    def _get_modifier_name(self, obj):

        return obj.modifier.name if obj.modifier else ''

    def _get_storage_places(self, obj):
        storage_places = obj.places.all()

        return resp.serialize_data(storage_places) if storage_places else []


class FaultSolutionSerializer(BaseModelSerializer):
    fault_type_title = serializers.SerializerMethodField('_get_fault_type_title')
    creator_name = serializers.SerializerMethodField('_get_creator_name')
    creator_dept_name = serializers.SerializerMethodField('_get_creator_dept_name')
    creator_contact = serializers.SerializerMethodField('_get_creator_contact')

    files = serializers.SerializerMethodField('_get_files')

    class Meta:
        model = FaultSolution
        fields = (
            'id', 'title', 'fault_type_id', 'fault_type_title', 'desc', 'solution', 'files',
            'creator_id', 'created_time', 'creator_name', 'creator_dept_name', 'creator_contact',
            'modifier_id', 'modified_time', 'auditor_id',  'audited_time'
        )

    def setup_eager_loading(queryset):
        return queryset

    def _get_fault_type_title(self, obj):
        return obj.fault_type.title if obj.fault_type else ''

    def _get_creator_name(self, obj):
        return obj.creator.name if obj.creator else ''

    def _get_creator_dept_name(self, obj):
        return obj.creator.dept.name if obj.creator and obj.creator.dept else ''

    def _get_creator_contact(self, obj):
        return obj.creator.contact if obj.creator else ''

    def _get_files(self, obj):
        if not obj.files:
            return []
        file_ids_str = obj.files.split(',')
        file_ids = [int(id_str) for id_str in file_ids_str]
        file_list = File.objects.filter(id__in=file_ids).all()
        return resp.serialize_data(file_list, srl_cls_name='FileSerializer') if file_list else []