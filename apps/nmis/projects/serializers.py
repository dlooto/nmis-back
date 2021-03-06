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
from nmis.projects.consts import PRO_DOC_CATE_OTHERS, \
    PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN, PRO_STATUS_DONE
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone, \
    ProjectMilestoneState, ProjectOperationRecord, ProjectDocument, SupplierSelectionPlan, \
    PurchaseContract, Receipt

logger = logging.getLogger(__name__)


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
    plan_files = serializers.SerializerMethodField('_get_plan_files')
    other_files = serializers.SerializerMethodField('_get_other_files')

    class Meta:
        model = SupplierSelectionPlan
        fields = (
            'id', 'project_milestone_state_id',
            'supplier_id', 'supplier_name', 'total_amount', 'plan_files', 'other_files',
            'remark', 'selected',
        )

    def _get_supplier_name(self, obj):
        return obj.supplier.name if obj.supplier else ''

    def _get_plan_files(self, obj):
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        plan_docs = ProjectDocument.objects.filter(id__in=doc_ids, category=PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN)
        return resp.serialize_data(plan_docs) if plan_docs else []

    def _get_other_files(self, obj):
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        other_docs = ProjectDocument.objects.filter(id__in=doc_ids, category=PRO_DOC_CATE_OTHERS)
        return resp.serialize_data(other_docs) if other_docs else []


class ProjectMilestoneStateSerializer(BaseModelSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    children = serializers.SerializerMethodField('_get_children')
    created_time = serializers.SerializerMethodField('_get_created_time')
    finished_time = serializers.SerializerMethodField('_get_finished_time')
    is_saved = serializers.SerializerMethodField('_is_saved_data')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'has_children', 'children',
            'status', 'created_time',
            'finished_time', 'is_saved', 'modified_time'
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
        if not hasattr(obj, 'created_time'):
            return ''
        return obj.created_time

    def _get_finished_time(self, obj):
        if not hasattr(obj, 'finished_time'):
            return ''
        return obj.finished_time

    def _get_children(self, obj):
        if not hasattr(obj, 'children'):
            return []
        children = obj.children
        return resp.serialize_data(children, srl_cls_name='ProjectMilestoneStateSerializer') if children else []

    def _is_saved_data(self, obj):
        """
        是否已保存数据
        当前逻辑：创建ProjectMilestoneState对象时并不保存额外的数据，保存额外数据时，更新modified_time字段
        :param obj:
        :return:
        """
        if not hasattr(obj, 'modified_time'):
            return False
        return True if obj and obj.modified_time else False


class ChunkProjectMilestoneStateSerializer(ProjectMilestoneStateSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    cate_documents = serializers.SerializerMethodField('_get_cate_documents')
    purchase_method = serializers.SerializerMethodField('_get_purchase_method')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'cate_documents', 'summary', 'purchase_method',
            'status', 'created_time', 'finished_time', 'is_saved', 'modified_time'
        )

    def _get_milestone_title(self, obj):
        stone = obj.milestone
        return stone.title if stone else ''

    def _get_milestone_index(self, obj):
        stone = obj.milestone
        return stone.index if stone else -1

    def _get_cate_documents(self, obj):
        """获取分类文档"""
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids).all()
        if not doc_list:
            return []

        cate_document_list = list()
        category_set = set()

        for doc in doc_list:
            category_set.add(doc.category)

        for category in category_set:
            cate_document = {'category': category}
            file_list = list()
            for doc in doc_list:
                if doc.category == category:
                    doc = {'id': doc.id, 'name': doc.name, 'path': doc.path, 'category': doc.category}
                    file_list.append(doc)
            cate_document['files'] = file_list
            cate_document_list.append(cate_document)

        return cate_document_list if cate_document_list else []

    def _get_purchase_method(self, obj):
        """
        获取采购方法
        """
        purchase_method = obj.get_project_purchase_method()
        return purchase_method if purchase_method else ''


class ProjectMilestoneStateWithSupplierSelectionPlanSerializer(ProjectMilestoneStateSerializer):
    supplier_selection_plans = serializers.SerializerMethodField('_get_supplier_selection_plans')

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_id',  'milestone_title',
            'milestone_index', 'created_time', 'is_saved',
            'status', 'summary', 'supplier_selection_plans', 'finished_time', 'modified_time'
        )

    def _get_supplier_selection_plans(self, obj):
        plans = SupplierSelectionPlan.objects.filter(project_milestone_state=obj)
        return resp.serialize_data(plans) if plans else []


class ProjectMilestoneStateWithSupplierSelectionPlanSelectedSerializer(ProjectMilestoneStateSerializer):
    supplier_selection_plans = SupplierSelectionPlanSerializer(many=True)
    cate_documents = serializers.SerializerMethodField('_get_cate_documents')


    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_id',  'milestone_title',
            'milestone_index', 'created_time', 'cate_documents',
            'status', 'summary', 'supplier_selection_plans', 'finished_time', 'is_saved',
            'modified_time'
        )

    def _get_cate_documents(self, obj):
        """获取分类文档"""
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids).all()
        if not doc_list:
            return []

        cate_document_list = list()
        category_set = set()

        for doc in doc_list:
            category_set.add(doc.category)

        for category in category_set:
            cate_document = {'category': category}
            file_list = list()
            for doc in doc_list:
                if doc.category == category:
                    doc = {'id': doc.id, 'name': doc.name, 'path': doc.path, 'category': doc.category}
                    file_list.append(doc)
            cate_document['files'] = file_list
            cate_document_list.append(cate_document)

        return cate_document_list if cate_document_list else []


class ProjectPlanSerializer(BaseModelSerializer):
    """
    简单项目序列化对象
    """

    creator_name = serializers.SerializerMethodField("_get_creator_name")
    performer_name = serializers.SerializerMethodField("_get_performer_name")
    assistant_name = serializers.SerializerMethodField("_get_assistant_name")
    related_dept_name = serializers.SerializerMethodField("_get_related_dept_name")
    current_stone_title = serializers.SerializerMethodField("_get_current_stone_title")

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
            'attached_flow_id', 'current_stone_id', 'current_stone_title',
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

    def _get_current_stone_title(self, obj):
        if obj.current_stone and obj.current_stone.milestone:
            if obj.status == PRO_STATUS_DONE:
                return '已完成'
            return obj.current_stone.milestone.title
        return ''


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

    # main_project_milestones = serializers.SerializerMethodField('_get_pro_main_milestone_states')
    project_milestone_states = serializers.SerializerMethodField('_get_pro_milestone_states_structured')
    current_stone_title = serializers.SerializerMethodField("_get_current_stone_title")


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
            'creator_id', 'creator_name','related_dept_id', 'related_dept_name',
            'performer_id', 'performer_name', 'assistant_id', 'assistant_name',
            'project_introduce', 'pre_amount', 'purchase_method', 'current_stone_id', 'current_stone_title',
            'attached_flow_id', 'project_milestone_states',
            'hardware_devices', 'software_devices',
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


    # def _get_pro_main_milestone_states(self, obj):
    #
    #     states = obj.get_main_milestone_states()
    #     return resp.serialize_data(states) if states else []


    def _get_pro_milestone_states_structured(self, obj):
        states = obj.get_project_milestone_states_structured()
        # return resp.serialize_data(states, srl_cls_name='ProjectMilestoneStateSerializer') if states else []
        return states

    def _get_projects_operation(self, obj):

        project_operation_record = ProjectOperationRecord.objects.get_reason(project_id=obj.id, status=obj.status)
        return resp.serialize_data(project_operation_record) if project_operation_record else []

    def _get_current_stone_title(self, obj):
        if obj.current_stone and obj.current_stone.milestone:
            if obj.status == PRO_STATUS_DONE:
                return '已完成'
            return obj.current_stone.milestone.title
        return ''


class ProjectDocumentSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectDocument
        fields = (
            'id', 'name', 'category', "path",
        )


class ProjectOperationRecordSerializer(BaseModelSerializer):

    class Meta:
        model = ProjectOperationRecord
        fields = '__all__'


class PurchaseContractSerializer(BaseModelSerializer):

    contract_devices = serializers.SerializerMethodField('_get_contract_devices')

    class Meta:
        model = PurchaseContract
        fields = ('id', 'created_time', 'contract_no', 'title', 'signed_date',
                  'buyer', 'buyer_contact', 'buyer_tel', 'seller', 'seller_contact',
                  'seller_tel', 'total_amount', 'delivery_date', 'contract_devices')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related(
            'contract_devices',
        )
        return queryset

    def _get_contract_devices(self, obj):
        return resp.serialize_data(obj.contract_devices.all())


class ProjectMilestoneStateAndPurchaseContractSerializer(ProjectMilestoneStateSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    cate_documents = serializers.SerializerMethodField('_get_cate_documents')
    purchase_method = serializers.SerializerMethodField('_get_purchase_method')

    purchase_contract = serializers.SerializerMethodField('_get_purchase_contract')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'cate_documents', 'summary', 'purchase_method',
            # 'has_children', 'children',
            'status', 'created_time', 'purchase_contract', 'is_saved',
            'modified_time'
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

    def _get_cate_documents(self, obj):
        """获取分类文档"""
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids).all()
        if not doc_list:
            return []

        cate_document_list = list()
        category_set = set()

        for doc in doc_list:
            category_set.add(doc.category)

        for category in category_set:
            cate_document = {'category': category}
            file_list = list()
            for doc in doc_list:
                if doc.category == category:
                    doc = {'id': doc.id, 'name': doc.name, 'path': doc.path, 'category': doc.category}
                    file_list.append(doc)
            cate_document['files'] = file_list
            cate_document_list.append(cate_document)

        return cate_document_list if cate_document_list else []

    def _get_purchase_contract(self, obj):

        purchase_contract = PurchaseContract.objects.get_purchase_contract_by_project_milestone_state(project_milestone_state=obj)

        return resp.serialize_data(purchase_contract) if purchase_contract else None

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


class ProjectMilestoneStateAndReceiptSerializer(ProjectMilestoneStateSerializer):

    milestone_title = serializers.SerializerMethodField('_get_milestone_title')
    milestone_index = serializers.SerializerMethodField('_get_milestone_index')
    cate_documents = serializers.SerializerMethodField('_get_cate_documents')
    purchase_method = serializers.SerializerMethodField('_get_purchase_method')

    receipt = serializers.SerializerMethodField('_get_receipt')

    @staticmethod
    def setup_eager_loading(queryset):
        return queryset.select_related('milestone',)

    class Meta:
        model = ProjectMilestoneState
        fields = (
            'id', 'milestone_title', 'milestone_index',
            'cate_documents', 'summary', 'purchase_method',
            # 'has_children', 'children',
            'status', 'created_time', 'receipt', 'is_saved', 'modified_time'
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

    def _get_cate_documents(self, obj):
        """获取分类文档"""
        if not obj.doc_list:
            return []
        doc_ids_str = obj.doc_list.split(',')
        doc_ids = [int(id_str) for id_str in doc_ids_str]
        doc_list = ProjectDocument.objects.filter(id__in=doc_ids).all()
        if not doc_list:
            return []

        cate_document_list = list()
        category_set = set()

        for doc in doc_list:
            category_set.add(doc.category)

        for category in category_set:
            cate_document = {'category': category}
            file_list = list()
            for doc in doc_list:
                if doc.category == category:
                    doc = {'id': doc.id, 'name': doc.name, 'path': doc.path, 'category': doc.category}
                    file_list.append(doc)
            cate_document['files'] = file_list
            cate_document_list.append(cate_document)

        return cate_document_list if cate_document_list else []

    def _get_receipt(self, obj):

        receipt = Receipt.objects.get_receipt_by_project_milestone_state(project_milestone_state=obj)

        return resp.serialize_data(receipt) if receipt else []

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


class ReceiptSerializer(BaseModelSerializer):

    class Meta:
        model = Receipt
        fields = (
            'id', 'served_date', 'delivery_man', 'contact_phone'
        )


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