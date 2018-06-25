# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging
import settings

from django.contrib import admin
from nmis.projects.models import ProjectFlow, ProjectMilestoneRecord

from .models import ProjectPlan, Milestone

logs = logging.getLogger(__name__)


class ProjectPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'creator', 'related_dept', 'performer',
        'current_stone', 'status', 'created_time'
    )


class ProjectFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'organ', 'title', 'type', 'pre_defined', 'created_time')

class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'flow', 'title', 'index', 'created_time')

class ProjectMilestoneRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'milestone', 'created_time')


admin.site.register(ProjectPlan, ProjectPlanAdmin)
admin.site.register(ProjectFlow, ProjectFlowAdmin)
admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(ProjectMilestoneRecord, ProjectMilestoneRecordAdmin)
