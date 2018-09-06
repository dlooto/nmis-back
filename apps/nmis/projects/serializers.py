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
    ProjectMilestoneRecord, ProjectOperationRecord, ProjectDocument

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
    #milestones = MilestoneSerializer(many=True)

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


class ProjectMilestoneRecordSerializer(BaseModelSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    doc_list = serializers.SerializerMethodField('_get_milestone_doc_list')
    purchase_method = serializers.SerializerMethodField('_get_purchase_method')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone')

    class Meta:
        model = ProjectMilestoneRecord
        fields = (
            'id', 'milestone_id', 'purchase_method', 'milestone_title',
            'milestone_index', 'created_time', 'doc_list',
            'finished', 'summary', 'purchase_method'
        )

    def _get_milestone_title(self, obj):
        stone = Milestone.objects.get_cached(obj.milestone_id)
        return stone.title if stone else ''

    def _get_milestone_index(self, obj):
        stone = Milestone.objects.get_cached(obj.milestone_id)
        return stone.index if stone else -1

    def _get_milestone_doc_list(self, obj):
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
        purchase_method = obj.get_project_purchase_method()
        return purchase_method if purchase_method else ''


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
    attached_flow = ProjectFlowSerializer(many=False)
    hardware_devices = serializers.SerializerMethodField('_get_hardware_devices')
    software_devices = serializers.SerializerMethodField('_get_software_devices')

    milestone_records = serializers.SerializerMethodField('_get_milestone_records')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related(
            'attached_flow', 'creator', 'related_dept', 'performer', 'assistant'
        )
        queryset = queryset.prefetch_related(
            'ordered_devices', 'software_devices',
            'project_milestone_records', 'attached_flow__milestones',
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
            'attached_flow', 'hardware_devices', 'software_devices', 'milestone_records',
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

    def _get_milestone_records(self, obj):
        # TODO: 已完成部分优化，还需优化，需要去掉根据流程ID查询milestone数据
        # records = obj.get_milestone_changed_records()
        # return resp.serialize_data(records) if records else []
        records = obj.project_milestone_records.all()
        return resp.serialize_data(records) if records else []

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