# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging


from rest_framework import serializers

from base import resp
from base.serializers import BaseModelSerializer
from nmis.hospitals.models import Staff, Department
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone, \
    ProjectMilestoneRecord

logs = logging.getLogger(__name__)


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
        staff = Staff.objects.get_cached(obj.creator_id)
        return staff.name if staff else ''

    def _get_performer_name(self, obj):
        if not obj.performer_id:
            return ''
        staff = Staff.objects.get_cached(obj.performer_id)
        return staff.name

    def _get_assistant_name(self, obj):
        if not obj.assistant_id:
            return ''
        staff = Staff.objects.get_cached(obj.assistant_id)
        return staff.name

    def _get_related_dept_name(self, obj):
        dept = Department.objects.get_cached(obj.related_dept_id)
        return dept.name

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

    attached_flow = serializers.SerializerMethodField('_get_attached_flow')
    ordered_devices = serializers.SerializerMethodField('_get_ordered_devices')

    milestone_records = serializers.SerializerMethodField('_get_milestone_records')

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'purpose', 'status', 'handing_type',
            'creator_id', 'creator_name',
            'related_dept_id', 'related_dept_name',
            'performer_id', 'performer_name', 'assistant_id', 'assistant_name',
            'current_stone_id', 'attached_flow', 'ordered_devices', 'milestone_records',
            'startup_time', 'expired_time', 'created_time',
        )

    def _get_creator_name(self, obj):
        staff = Staff.objects.get_cached(obj.creator_id)
        return staff.name if staff else ''

    def _get_performer_name(self, obj):
        if not obj.performer_id:
            return ''
        staff = Staff.objects.get_cached(obj.performer_id)
        return staff.name

    def _get_assistant_name(self, obj):
        if not obj.assistant_id:
            return ''
        staff = Staff.objects.get_cached(obj.assistant_id)
        return staff.name

    def _get_related_dept_name(self, obj):
        dept = Department.objects.get_cached(obj.related_dept_id)
        return dept.name

    def str_startup_time(self, obj):
        return self.str_time_obj(obj.startup_time)

    def str_expired_time(self, obj):
        return self.str_time_obj(obj.expired_time)

    def _get_attached_flow(self, obj):
        if not obj.attached_flow:
            return {}
        flow = ProjectFlow.objects.get_cached(obj.attached_flow_id)
        return resp.serialize_data(flow)

    def _get_ordered_devices(self, obj):
        return resp.serialize_data(obj.get_ordered_devices())

    def _get_milestone_records(self, obj):  # TODO: 需要优化性能...
        records = obj.get_milestone_changed_records()
        return resp.serialize_data(records) if records else []


class ProjectFlowSerializer(BaseModelSerializer):

    milestones = serializers.SerializerMethodField('_get_milestones')

    class Meta:
        model = ProjectFlow
        fields = (
            'id', 'organ_id', 'title', 'type', 'pre_defined', 'milestones'
        )

    def _get_milestones(self, obj):
        return resp.serialize_data(obj.get_milestones())


class MilestoneSerializer(BaseModelSerializer):
    class Meta:
        model = Milestone
        fields = (
            'id', 'title', 'index', 'flow_id', 'desc', 'created_time',
        )

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
