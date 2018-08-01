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
    ProjectMilestoneRecord

logs = logging.getLogger(__name__)


class MilestoneSerializer(BaseModelSerializer):

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('flow')
        return queryset

    class Meta:
        model = Milestone
        fields = (
            'id', 'title', 'index', 'flow_id', 'desc', 'created_time',
        )


class ProjectFlowSerializer(BaseModelSerializer):
    milestones = serializers.SerializerMethodField('_get_milestones')

    class Meta:
        model = ProjectFlow
        fields = (
            'id', 'organ_id', 'title', 'type', 'pre_defined', 'milestones'
        )

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related()
        return queryset

    def _get_milestones(self, obj):
        return resp.serialize_data(obj.get_milestones())


class ProjectMilestoneRecordSerializer(BaseModelSerializer):
    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')

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
        queryset = queryset.prefetch_related('attached_flow')
        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('related_dept')
        queryset = queryset.select_related('performer')
        queryset = queryset.select_related('assistant')
        return queryset

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'handing_type', 'purpose', 'status',
            'creator_id', 'creator_name', 'related_dept_id', 'related_dept_name',
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

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('attached_flow')
        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('related_dept')
        queryset = queryset.select_related('performer')
        queryset = queryset.select_related('assistant')
        return queryset

    creator_name = serializers.SerializerMethodField("_get_creator_name")
    performer_name = serializers.SerializerMethodField("_get_performer_name")
    assistant_name = serializers.SerializerMethodField("_get_assistant_name")
    related_dept_name = serializers.SerializerMethodField("_get_related_dept_name")

    startup_time = serializers.SerializerMethodField("str_startup_time")
    expired_time = serializers.SerializerMethodField("str_expired_time")

    # attached_flow = serializers.SerializerMethodField('_get_attached_flow')
    attached_flow = ProjectFlowSerializer(many=False)
    hardware_devices = serializers.SerializerMethodField('_get_hardware_devices')
    software_devices = serializers.SerializerMethodField('_get_software_devices')

    milestone_records = serializers.SerializerMethodField('_get_milestone_records')

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'purpose', 'status', 'handing_type', 'project_cate',
            'creator_id', 'creator_name',
            'related_dept_id', 'related_dept_name',
            'performer_id', 'performer_name', 'assistant_id', 'assistant_name',
            'current_stone_id', 'attached_flow', 'hardware_devices', 'software_devices',
            'milestone_records', 'startup_time', 'expired_time', 'created_time'
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

    # def _get_attached_flow(self, queryset):
    #     return resp.serialize_data(queryset.attached_flow)

    def _get_hardware_devices(self, obj):
        return resp.serialize_data(obj.get_hardware_devices())

    def _get_software_devices(self, obj):
        return resp.serialize_data(obj.get_software_devices())

    def _get_milestone_records(self, obj):  # TODO: 需要优化性能...
        records = obj.get_milestone_changed_records()
        return resp.serialize_data(records) if records else []


class ProjectStatusCountSerializers(BaseModelSerializer):
    """
    返回项目各状态条数数据结构，该结构添加到最终的json响应结果里
    :return: 返回数据形如:
        "project_status_count": {
            "project_pending_count": 17,    项目待启动数量
            "project_started_count": 0,     项目进行中数量
            "project_down_count": 0         项目完成数量
        }
    """
    projects_status_count = 'project_status_count'  # 项目数量块标示
    project_started_count = 'project_started_count'  # 进行中项目数量
    project_pending_count = 'project_pending_count'  # 待启动项目数量
    project_done_count = 'project_done_count'  # 已完成的项目数量

    def get_project_status_count(self, **data):
        return {
            self.projects_status_count: OrderedDict([
                (self.project_pending_count, data.get('PE')),
                (self.project_started_count, data.get('SD')),
                (self.project_done_count, data.get('DO'))
                ])
        }
