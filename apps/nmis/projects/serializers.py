# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from collections import OrderedDict

from rest_framework import serializers

from base import resp
from base.serializers import BaseModelSerializer
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone, \
    ProjectMilestoneState, ProjectOperationRecord, ProjectDocument, SupplierSelectionPlan

logs = logging.getLogger(__name__)


class MilestoneSerializer(BaseModelSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('flow')
        return queryset

    class Meta:
        model = Milestone
        fields = (
            'id', 'title', 'index', 'flow_id', 'desc', 'parent_id', 'parent_path', 'created_time',
        )


class ProjectFlowSerializer(BaseModelSerializer):
    milestones = serializers.SerializerMethodField('_get_milestones')
    # milestones = MilestoneSerializer(many=True)

    class Meta:
        model = ProjectFlow
        fields = (
            'id', 'organ_id', 'title', 'type', 'pre_defined', 'milestones'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('milestones')
        return queryset

    def _get_milestones(self, obj):
        """
        当前流程的主里程碑
        """
        return resp.serialize_data(obj.get_main_milestones())


class SupplierSelectionPlanSerializer(BaseModelSerializer):
    supplier_name = serializers.SerializerMethodField('_get_supplier_name')
    doc_list = serializers.SerializerMethodField('_get_plan_doc_list')

    class Meta:
        model = SupplierSelectionPlan
        fields = (
            'id', 'project_milestone_state_id',
            'supplier_id', 'supplier_name', 'total_amount',
            'remark', 'doc_list', 'selected',
        )

    def _get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''

    def _get_plan_doc_list(self, obj):
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids)
        return resp.serialize_data(doc_list) if doc_list else []


class ProjectMilestoneStateSerializer(BaseModelSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    children = serializers.SerializerMethodField('_get_children')
    created_time = serializers.SerializerMethodField('_get_created_time')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'has_children', 'children', 'status', 'created_time',
        )

    def _get_milestone_title(self, obj):
        if not hasattr(obj, 'milestone'):
            return ''
        stone = obj.milestone
        return stone.title if stone else ''

    def _get_milestone_index(self, obj):
        if not hasattr(obj, 'milestone'):
            return ''
        stone = obj.milestone
        return stone.index if stone else -1

    def _get_created_time(self, obj):
        """

        :param obj:
        :return:
        """
        if not hasattr(obj, 'created_time'):
            return ''
        return obj.created_time

    def _get_children(self, obj):
        if not hasattr(obj, 'children'):
            return []
        children = obj.children
        return resp.serialize_data(children, srl_cls_name='ProjectMilestoneStateSerializer') if children else []


class ChunkProjectMilestoneStateSerializer(ProjectMilestoneStateSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    doc_list = serializers.SerializerMethodField('_get_doc_list')
    purchase_method = serializers.SerializerMethodField('_get_purchase_method')
    children = serializers.SerializerMethodField('_get_children')
    created_time = serializers.SerializerMethodField('_get_created_time')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'doc_list', 'summary', 'purchase_method',
            'has_children', 'children', 'status', 'created_time',
        )

    def _get_milestone_title(self, obj):
        if not hasattr(obj, 'milestone'):
            return ''
        stone = obj.milestone
        return stone.title if stone else ''

    def _get_milestone_index(self, obj):
        if not hasattr(obj, 'milestone'):
            return ''
        stone = obj.milestone
        return stone.index if stone else -1

    def _get_doc_list(self, obj):
        if not hasattr(obj, 'doc_list'):
            return []
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids)
        return resp.serialize_data(doc_list) if doc_list else []

    def _get_purchase_method(self, obj):
        """
        获取采购方法
        """
        if not hasattr(obj, 'get_project_purchase_method'):
            return ''
        purchase_method = obj.get_project_purchase_method()
        return purchase_method if purchase_method else ''

    def _get_created_time(self, obj):
        """

        :param obj:
        :return:
        """
        if not hasattr(obj, 'created_time'):
            return ''
        return obj.created_time

    def _get_children(self, obj):
        if not hasattr(obj, 'children'):
            return []
        children = obj.children
        return resp.serialize_data(children, srl_cls_name='ProjectMilestoneStateSerializer') if children else []


class ProjectMilestoneStateWithSupplierSelectionPlanSerializer(ProjectMilestoneStateSerializer):
    supplier_selection_plans = serializers.SerializerMethodField('_get_supplier_selection_plans')

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_id',  'milestone_title',
            'milestone_index', 'created_time', 'doc_list',
            'status', 'summary', 'supplier_selection_plans'
        )

    def _get_supplier_selection_plans(self, obj):
        plans = SupplierSelectionPlan.objects.filter(project_milestone_state=obj)
        return resp.serialize_data(plans) if plans else []


class ProjectMilestoneStateWithSupplierSelectionPlanSelectedSerializer(ProjectMilestoneStateSerializer):
    supplier_selection_plans = SupplierSelectionPlanSerializer(many=True)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_id',  'milestone_title',
            'milestone_index', 'created_time', 'doc_list',
            'status', 'summary', 'supplier_selection_plans'
        )


class ProjectPlanSerializer(BaseModelSerializer):
    """
    简单项目序列化对象
    """

    creator_name = serializers.SerializerMethodField("_get_creator_name")
    performer_name = serializers.SerializerMethodField("_get_performer_name")
    assistant_name = serializers.SerializerMethodField("_get_assistant_name")
    related_dept_name = serializers.SerializerMethodField("_get_related_dept_name")

    startup_time = serializers.SerializerMethodField("str_startup_time")
    expired_time = serializers.SerializerMethodField("str_expired_time")

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related(
            'attached_flow', 'creator', 'related_dept', 'performer', 'assistant',
        )
        return queryset

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'handing_type', 'purpose', 'status',
            'creator_id', 'creator_name', 'related_dept_id', 'related_dept_name',
            'project_introduce', 'pre_amount', 'purchase_method',
            'performer_id', 'performer_name', 'assistant_id', 'assistant_name',
            'attached_flow_id', 'current_stone_id',
            'startup_time', 'expired_time', 'created_time',
        )

    def _get_creator_name(self, obj):
        staff = obj.creator
        return staff.name if staff else ''

    def _get_performer_name(self, obj):
        if not obj.performer:
            return ''
        staff = obj.performer
        return staff.name

    def _get_assistant_name(self, obj):
        if not obj.assistant:
            return ''
        staff = obj.assistant
        return staff.name

    def _get_related_dept_name(self, obj):
        dept = obj.related_dept
        return dept.name if dept else ''

    def str_startup_time(self, obj):
        return self.str_time_obj(obj.startup_time)

    def str_expired_time(self, obj):
        return self.str_time_obj(obj.expired_time)


class ChunkProjectPlanSerializer(BaseModelSerializer):
    """
    复杂项目申请对象, 返回项目对象中内含设备明细
    """

    creator_name = serializers.SerializerMethodField("_get_creator_name")
    performer_name = serializers.SerializerMethodField("_get_performer_name")
    assistant_name = serializers.SerializerMethodField("_get_assistant_name")
    related_dept_name = serializers.SerializerMethodField("_get_related_dept_name")

    startup_time = serializers.SerializerMethodField("str_startup_time")
    expired_time = serializers.SerializerMethodField("str_expired_time")

    operation_record = serializers.SerializerMethodField("_get_projects_operation")

    # attached_flow = serializers.SerializerMethodField('_get_attached_flow')
    # attached_flow = ProjectFlowSerializer(many=False)
    hardware_devices = serializers.SerializerMethodField('_get_hardware_devices')
    software_devices = serializers.SerializerMethodField('_get_software_devices')

    # project_milestones = serializers.SerializerMethodField('_get_milestone_states')
    # main_project_milestones = serializers.SerializerMethodField('_get_pro_main_milestone_states')
    project_milestone_states = serializers.SerializerMethodField('_get_pro_milestone_states_structured')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related(
            'attached_flow', 'creator', 'related_dept', 'performer', 'assistant'
        )
        queryset = queryset.prefetch_related(
            'ordered_devices', 'software_devices',
            'pro_milestone_states_related', 'attached_flow__milestones',
        )
        return queryset

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'purpose', 'status', 'handing_type', 'project_cate',
            'creator_id', 'creator_name',
            'related_dept_id', 'related_dept_name',
            'performer_id', 'performer_name', 'assistant_id', 'assistant_name',
            'project_introduce', 'pre_amount', 'purchase_method', 'current_stone_id',
            'attached_flow_id', 'project_milestone_states', 'hardware_devices', 'software_devices',
            'startup_time', 'expired_time', 'created_time', 'operation_record',
        )

    def _get_creator_name(self, obj):
        staff = obj.creator
        return staff.name if staff else ''

    def _get_performer_name(self, obj):
        if not obj.performer:
            return ''
        staff = obj.performer
        return staff.name

    def _get_assistant_name(self, obj):
        if not obj.assistant:
            return ''
        staff = obj.assistant
        return staff.name

    def _get_related_dept_name(self, obj):
        dept = obj.related_dept
        return dept.name if dept else ''

    def str_startup_time(self, obj):
        return self.str_time_obj(obj.startup_time)

    def str_expired_time(self, obj):
        return self.str_time_obj(obj.expired_time)

    # def _get_attached_flow(self, obj):
    #     return resp.serialize_data(obj.attached_flow)

    def _get_hardware_devices(self, obj):
        # return resp.serialize_data(obj.get_hardware_devices())
        return resp.serialize_data(obj.ordered_devices.all())

    def _get_software_devices(self, obj):
        # return resp.serialize_data(obj.get_software_devices())
        return resp.serialize_data(obj.software_devices.all())

    def _get_pro_main_milestone_states(self, obj):

        states = obj.pro_milestone_states_related.all()
        main_milestone_states = []
        for state in states:
            if state.milestone.parent is None:
                main_milestone_states.append(state)
        return resp.serialize_data(main_milestone_states) if states else []

    def _get_pro_milestone_states_structured(self, obj):
        states = obj.get_project_milestone_states_structured()
        return resp.serialize_data(states) if states else []


    def _get_milestone_states(self, obj):
        pro_milestone_states = obj.pro_milestone_states_related.all()
        return resp.serialize_data(pro_milestone_states) if pro_milestone_states else []

    def _get_projects_operation(self, obj):

        project_operation_record = ProjectOperationRecord.objects.get_reason(project_id=obj.id, status=obj.status)
        return resp.serialize_data(project_operation_record) if project_operation_record else []


class ProjectDocumentSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectDocument
        fields = (
            'id', 'name', 'category',
        )


class ProjectOperationRecordSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectOperationRecord
        fields = '__all__'


def get_project_status_count(**data):

    """
    返回项目各个状态数量序列化字段
    """
    projects_status_count = 'project_status_count'  # 项目数量块标示
    project_started_count = 'project_started_count'  # 进行中项目数量
    project_pending_count = 'project_pending_count'  # 待启动项目数量
    project_done_count = 'project_done_count'  # 已完成的项目数量
    project_overruled_count = 'project_overruled_count'  # 待启动项目数量
    project_paused_count = 'project_paused_count'  # 已完成的项目数量

    if not data.get('SD'):
        data['SD'] = 0
    if not data.get('PE'):
        data['PE'] = 0
    if not data.get('DO'):
        data['DO'] = 0
    if not data.get('OR'):
        data['OR'] = 0
    if not data.get('PA'):
        data['PA'] = 0

    return {
        projects_status_count: OrderedDict([
            (project_pending_count, data.get('PE')),
            (project_started_count, data.get('SD')),
            (project_done_count, data.get('DO')),
            (project_overruled_count, data.get('OR')),
            (project_paused_count, data.get('PA'))
        ])
    }