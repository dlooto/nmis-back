# coding=utf-8
#
# Created by junn, on 2018-6-6
#

"""

"""

import logging

from django.contrib import admin
from nmis.projects.models import ProjectFlow, ProjectMilestoneState, ProjectDocument, \
    Supplier, SupplierSelectionPlan, PurchaseContract, Receipt

from .models import ProjectPlan, Milestone

logger = logging.getLogger(__name__)


class ProjectPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'project_cate', 'handing_type',
        'creator', 'related_dept', 'performer',
        'current_stone', 'status', 'created_time'
    )


class ProjectFlowAdmin(admin.ModelAdmin):
    list_display = ('id', 'organ', 'title', 'type', 'pre_defined', 'default_flow', 'created_time')


class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'flow', 'title', 'index', 'parent', 'parent_path', 'created_time')


class ProjectMilestoneStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'milestone', 'doc_list', 'summary', 'status', 'created_time')


class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'path',)
    search_fields = ('name', 'category')
    list_filter = ('category', )


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'contact_tel', )
    search_fields = ('name',)


class SupplierSelectionPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_milestone_state', 'supplier', 'total_amount', 'remark', 'selected')
    search_fields = ('project_milestone_state', 'supplier')
    list_display_links = ('project_milestone_state', 'supplier')
    list_filter = ('selected', )


class PurchaseContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'project_milestone_state', 'contract_no', 'title', 'buyer', 'seller', 'total_amount')
    search_fields = ('contract_no', 'title')
    list_display_links = ('project_milestone_state',)
    list_filter = ('buyer', 'seller', 'total_amount')


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'served_date', 'delivery_man', 'contact_phone', )
    list_filter = ('served_date',)


admin.site.register(ProjectPlan, ProjectPlanAdmin)
admin.site.register(ProjectFlow, ProjectFlowAdmin)
admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(ProjectMilestoneState, ProjectMilestoneStateAdmin)
admin.site.register(ProjectDocument, ProjectDocumentAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SupplierSelectionPlan, SupplierSelectionPlanAdmin)
admin.site.register(PurchaseContract, PurchaseContractAdmin)
admin.site.register(Receipt, ReceiptAdmin)

