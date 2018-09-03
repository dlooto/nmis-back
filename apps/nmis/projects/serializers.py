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
    ProjectMilestoneRecord, ProjectOperationRecord

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
        return resp.serialize_data(obj.milestones.all())


class ProjectMilestoneRecordSerializer(BaseModelSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone')

    class Meta:
        model = ProjectMilestoneRecord
        fields = (
            'id', 'milestone_id', 'milestone_title', 'milestone_index', 'created_time',
        )

    def _get_milestone_title(self, obj):
        stone = Milestone.objects.get_cached(obj.milestone_id)
        return stone.title if stone else ''

    def _get_milestone_index(self, obj):
        stone = Milestone.objects.get_cached(obj.milestone_id)
        return stone.index if stone else -1


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
            'project_introduce', 'pre_amount', 'procurement_method',
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
            'project_introduce', 'pre_amount', 'procurement_method', 'current_stone_id',
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


class ProjectOperationRecordSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectOperationRecord
        fields = '__all__'
