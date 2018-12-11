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
    list_display_links = ('id', 'title', 'project_cate')
    list_filter = ('project_cate', 'handing_type', 'status')
    search_fields = ('id', 'title', 'desc')


class ProjectFlowAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'type', 'pre_defined', 'default_flow', 'organ',  'created_time')
    list_display_links = ('id', 'title', )
    list_filter = ('type', 'pre_defined', 'default_flow')
    search_fields = ('id', 'title')


class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'index', 'parent', 'parent_path', 'flow', 'created_time')
    list_display_links = ('id', 'title')
    list_filter = ('flow__title',)
    search_fields = ('id', 'title')


class ProjectMilestoneStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'milestone', 'doc_list', 'summary', 'status', 'created_time')
    list_display_links = ('id', 'project', )
    list_filter = ('project__title', 'status',)
    search_fields = ('id', 'project__title')


class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'path',)
    list_display_links = ('id', 'name', )
    search_fields = ('id', 'name', 'category')
    list_filter = ('category', )


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'contact_tel', )
    list_display_links = ('id', 'name', )
    list_filter = ()
    search_fields = ('id', 'name')


class SupplierSelectionPlanAdmin(admin.ModelAdmin):
    list_display = ('id',  'supplier', 'total_amount', 'remark', 'selected', 'project_milestone_state')
    list_display_links = ('supplier', )
    search_fields = ('project_milestone_state', 'supplier')
    list_filter = ('selected', 'project_milestone_state__project__title')


class PurchaseContractAdmin(admin.ModelAdmin):
    list_display = ('id',  'contract_no', 'title', 'buyer', 'seller', 'total_amount', 'project_milestone_state',)
    list_display_links = ('contract_no', 'title')
    search_fields = ('contract_no', 'title')
    list_filter = ('project_milestone_state__project__title', )


class ReceiptAdmin(admin.ModelAdmin):
    list_display = ('id', 'served_date', 'delivery_man', 'contact_phone', )
    list_display_links = ('id',)
    list_filter = ()
    search_fields = ('id', 'delivery_man')


admin.site.register(ProjectPlan, ProjectPlanAdmin)
admin.site.register(ProjectFlow, ProjectFlowAdmin)
admin.site.register(Milestone, MilestoneAdmin)
admin.site.register(ProjectMilestoneState, ProjectMilestoneStateAdmin)
admin.site.register(ProjectDocument, ProjectDocumentAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SupplierSelectionPlan, SupplierSelectionPlanAdmin)
admin.site.register(PurchaseContract, PurchaseContractAdmin)
admin.site.register(Receipt, ReceiptAdmin)

