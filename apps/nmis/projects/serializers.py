# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging


from rest_framework import serializers

from base import resp
from base.serializers import BaseModelSerializer
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone

logs = logging.getLogger(__name__)


class ProjectPlanSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectPlan
        fields = '__all__'


class ChunkProjectPlanSerializer(BaseModelSerializer):
    """
    复杂项目申请对象, 返回项目对象中内含设备明细
    """

    ordered_devices = serializers.SerializerMethodField('_get_ordered_devices')

    class Meta:
        model = ProjectPlan
        fields = (
            'id', 'title', 'purpose', 'status', 'creator', 'related_dept',
            'performer', 'current_stone', 'ordered_devices', 'created_time'
        )

    def _get_ordered_devices(self, obj):
        return resp.serialize_data(obj.get_ordered_devices()) if obj else []


class ProjectFlowSerializer(BaseModelSerializer):

    milestones = serializers.SerializerMethodField('_get_milestones')

    class Meta:
        model = ProjectFlow
        fields = (
            'id', 'hospital', 'title', 'type', 'pre_defined', 'milestones'
        )

    def _get_milestones(self, obj):
        return resp.serialize_data(obj.get_milestones()) if obj else []


class MilestoneSerializer(BaseModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
