# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging


from rest_framework import serializers

from base.serializers import BaseModelSerializer
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone

logs = logging.getLogger(__name__)


class ProjectPlanSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectPlan
        fields = '__all__'


class ProjectFlowSerializer(BaseModelSerializer):
    class Meta:
        model = ProjectFlow
        fields = '__all__'


class MilestoneSerializer(BaseModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'
