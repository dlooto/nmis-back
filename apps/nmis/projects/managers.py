# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging

from django.db import transaction, DataError, models
from django_bulk_update import helper

from base.models import BaseManager
from nmis.devices.models import OrderedDevice, SoftwareDevice, ContractDevice
from nmis.projects.consts import (PRO_CATE_HARDWARE, PRO_CATE_SOFTWARE,
                                  PRO_STATUS_STARTED, PRO_STATUS_OVERRULE,
                                  PRO_STATUS_PAUSE, PRO_OPERATION_OVERRULE,
                                  PRO_OPERATION_PAUSE, PRO_STATUS_DONE,
                                  PRO_STATUS_PENDING,)

logger = logging.getLogger(__name__)


class ProjectPlanManager(BaseManager):

    def create_project(self, hardware_devices=None, software_devices=None, **data):
        """
        创建项目项目(新建信息化硬件项目，新建信息化软件项目)

        :param hardware_devices: 硬件设备明细, 列表数据, 列表元素类型为dict
        :param software_devices: 软件设备明细, 列表数据, 列表元素类型为dict
        :param data: 字典型参数
        :return:
        """
        try:
            with transaction.atomic():
                project = self.model(**data)
                project.save()

                # 批量创建设备明细
                ordered_device_list = []
                if data.get('project_cate') == PRO_CATE_HARDWARE:
                    for device_data in hardware_devices:
                        ordered_device_list.append(
                            OrderedDevice(project=project, **device_data)
                        )
                    OrderedDevice.objects.bulk_create(ordered_device_list)

                else:
                    if hardware_devices:
                        for device_data in hardware_devices:
                            ordered_device_list.append(
                                OrderedDevice(project=project, **device_data)
                            )
                        OrderedDevice.objects.bulk_create(ordered_device_list)
                    if software_devices:
                        ordered_device_list = []
                        for device_data in software_devices:
                            ordered_device_list.append(
                                SoftwareDevice(project=project, **device_data)
                            )
                        SoftwareDevice.objects.bulk_create(ordered_device_list)
        except DataError as dex:
            logger.exception(dex)
            return None
        except Exception as e:
            logger.exception(e)
            return None
        return project

    # def get_allot_projects(self):
    #     return self.filter(performer=None)

    def get_undispatched_projects(self, dept_id_list, organ, project_title=None, creators=None):
        """
        按关键字(项目名/项目申请人)查询机构所有待分配的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ, related_dept_id__in=dept_id_list, status=PRO_STATUS_PENDING)
        if project_title or creators:
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(creator__in=creators)
            ).distinct()
        return query_set.order_by('-created_time')

    def get_dispatched_projects(self, dept_id_list, organ):
        """
        获取已分配项目列表
        """
        query_set = self.filter(
            related_dept__organ=organ, related_dept_id__in=dept_id_list,
            status__in=[PRO_STATUS_STARTED, PRO_STATUS_PAUSE])

        return query_set.order_by('-created_time')

    def get_by_search_key(self, organ, project_title=None, performers=None, status=None):
        """
        按关键字(项目名/项目负责人)查询机构所有的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ)
        if status:
            query_set = query_set.filter(status=status)
        if project_title or performers:
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(performer__in=performers)
            ).distinct()
        return query_set.order_by('-created_time')

    def get_applied_projects(self, organ, staff, performers=None, project_title=None, status=None):
        """
        按关键字:(项目名/项目负责人)查询机构所有我的申请项目列表
        :param organ: 项目申请者所有机构
        :param staff: 当前登录系统用户
        :param performers: 项目负责人Staff集合
        :param project_title: 项目名称
        :param status 项目状态
        """
        query_set = self.filter(related_dept__organ=organ, creator=staff)
        if status:
            query_set = query_set.filter(status=status)
        if performers or project_title:
            from django.db.models import Q
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(performer__in=performers)
            ).distinct()
        return query_set.order_by('-created_time')

    def get_my_performer_projects(self, organ, staff, creators=None, project_title=None, status=None):
        """
        按关键字:(项目名/项目申请人)查询机构所有我负责的项目列表
        :param organ:
        :param staff: 当前登录系统用户
        :param project_title: 项目名称
        :param creators: 项目申请人Staff集合
        :param status: 项目状态
        :param
        """
        query_set = self.filter(related_dept__organ=organ, performer=staff)
        if status:
            query_set = query_set.filter(status=status)
        if project_title or creators:
            from django.db.models import Q
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(creator__in=creators)
            ).distinct()
        return query_set.order_by('-created_time')

    def get_my_assistant_projects(self, organ, assistant, performer=None, project_title=None, status=None):
        """
        按关键字:(项目名/项目申请人)查询机构所有我协助的项目列表
        :param organ:
        :param assistant: 项目协助人
        :param performer: 项目负责人
        :param project_title: 项目名称
        :param status: 项目状态
        """
        query_set = self.filter(related_dept__organ=organ, assistant=assistant)
        if status:
            query_set = query_set.filter(status=status)
        if project_title or performer:
            from django.db.models import Q
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(performer__in=performer)
            ).distinct()

        return query_set.order_by('-created_time')

    def start_project(self):
        """
        TODO:
        """
        pass

    def update_project(self, old_project, **data):
        """
        TODO:
        :param old_project:
        :return:
        """

        try:
            with transaction.atomic():
                pro_base_data = {}
                if data.get('title'):
                    pro_base_data['title'] = data.get('title')
                if data.get('handing_type'):
                    pro_base_data['handing_type'] = data.get('handing_type')
                if data.get('purpose'):
                    pro_base_data['purpose'] = data.get('purpose')
                if data.get('project_introduce'):
                    pro_base_data['project_introduce'] = data.get('project_introduce').strip()
                if pro_base_data:
                    new_project = old_project.update(pro_base_data)

                if data.get('hardware_added_devices'):
                    # 批量添加新增的医疗器械设备明细
                    hardware_device_list = []
                    for device_data in data.get('hardware_added_devices'):
                        hardware_device_list.append(
                            OrderedDevice(project=old_project, **device_data)
                        )
                    OrderedDevice.objects.bulk_create(hardware_device_list)

                if data.get('hardware_updated_devices'):
                    # 批量修改医疗器械设备明细
                    hardware_updated_device_list = sorted(data.get('hardware_updated_devices'), key=lambda item: item['id'])
                    hardware_updated_id_list = [update_device['id'] for update_device in hardware_updated_device_list]

                    devices = OrderedDevice.objects.filter(pk__in=hardware_updated_id_list).order_by("id")
                    for i in range(len(devices)):
                        devices[i].name = hardware_updated_device_list[i].get('name')
                        devices[i].num = hardware_updated_device_list[i].get('num')
                        devices[i].planned_price = hardware_updated_device_list[i].get('planned_price')
                        devices[i].measure = hardware_updated_device_list[i].get('measure')
                        devices[i].purpose = hardware_updated_device_list[i].get('purpose')
                        devices[i].type_spec = hardware_updated_device_list[i].get('type_spec')
                    helper.bulk_update(devices)

                if old_project.project_cate == PRO_CATE_SOFTWARE:
                    if data.get('software_added_devices'):
                        # 批量添加新增的信息化设备明细
                        software_added_device_list = []
                        for device_data in data.get('software_added_devices'):
                            software_added_device_list.append(
                                SoftwareDevice(project=old_project, **device_data)
                            )
                        SoftwareDevice.objects.bulk_create(software_added_device_list)
                    if data.get('software_updated_devices'):
                        # 批量修改信息化设备
                        software_update_device_list = sorted(
                            data.get('software_updated_devices'), key=lambda item: item['id']
                        )
                        software_updated_id_list = [software['id'] for software in software_update_device_list]
                        software_old_device_list = SoftwareDevice.objects.filter(pk__in=software_updated_id_list).order_by('id')
                        for i in range(len(software_old_device_list)):
                            software_old_device_list[i].name = software_update_device_list[i].get('name')
                            software_old_device_list[i].purpose = software_update_device_list[i].get('purpose')
                        helper.bulk_update(software_old_device_list)
        except Exception as e:
            logger.exception(e)
            return None

        return new_project

    def get_group_by_status(self, search_key=None, creator=None, performer=None, assistant=None):
        """
        根据项目状态返回每个状态下项目数量(项目总览各状态条数，我申请的项目各状态条数，我负责的各状态条数)
        :return:
        """
        results = self.filter(title__contains=search_key).values_list('status').annotate(
            models.Count('id'))
        if creator:
            results = self.filter(creator=creator, title__contains=search_key)\
                .values_list('status').annotate(models.Count('id'))
        if performer:
            results = self.filter(performer=performer, title__contains=search_key)\
                .values_list('status').annotate(models.Count('id'))
        if assistant:
            results = self.filter(assistant=assistant, title__contains=search_key)\
                .values_list('status').annotate(models.Count('id'))
        return results


class MilestoneManager(BaseManager):
    pass


class ProjectFlowManager(BaseManager):

    def create_flow(self, milestones, **data):
        """
        创建项目流程
        :param milestones:
        :param data:
        :return:
        """
        from .models import Milestone

        try:
            with transaction.atomic():
                flow = self.model(**data)
                flow.save()

                milestone_list = []
                for ms in milestones:
                    milestone_list.append(Milestone(flow=flow, **ms))
                Milestone.objects.bulk_create(milestone_list)
        except Exception as e:
            logger.exception(e)
            return None

        return flow

    def get_default_flow(self):
        """获取默认流程"""
        flow = self.filter(default_flow=True).first()
        return flow if flow else None


class ProjectOperationRecordManager(BaseManager):

    def add_operation_records(self, **data):
        project_operation_record = self.model(**data)
        project_operation_record.save()
        project_operation_record.cache()

        return project_operation_record

    def get_reason(self, project_id, status):
        """
        获取项目被挂起/被驳回的原因
        :param project_id: 项目ID
        :param status: 项目状态
        """
        if status == PRO_STATUS_OVERRULE:

            project_operation_record = self.filter(
                project=project_id, operation=PRO_OPERATION_OVERRULE
            ).order_by("-created_time")

        else:
            project_operation_record = self.filter(
                project=project_id, operation=PRO_OPERATION_PAUSE
            ).order_by('-created_time')

        return project_operation_record

    def get_operation(self, project_id):
        """
        获取项目被挂起/被驳回的操作方式
        :param project_id: 查看项目ID
        """
        project_operation_record = self.filter(project=project_id).first()

        if project_operation_record:
            return project_operation_record.operation
        return None


class ProjectDocumentManager(BaseManager):

    def get_project_document(self, name, category):
        return self.filter(name=name, category=category).first()

    def add_project_document(self, name, category, path):
        old_doc = self.get_project_document(name, category)
        if old_doc:
            return False, '已存在相同资料类别的同名文件'
        doc = self.model(name=name, category=category, path=path)
        doc.save()
        doc.cache()
        return True, doc

    def update_project_document(self, ):
        pass

    def bulk_create_project_docs(self, files):
        try:
            with transaction.atomic():
                import os
                project_documents = []
                for file in files:
                    for file_path in file.get('file_paths'):
                        project_documents.append(
                            self.model(
                                name=os.path.basename(file_path),
                                path=file_path,
                                category=file.get('file_category')
                            )
                        )
                self.bulk_create(project_documents)
        except Exception as e:
            logger.exception(e)
            return False
        return True

    def batch_save_upload_project_doc(self, tag_upload_result_dict):
        """
        批量保存或更新上传的project_document
        :param tag_upload_result_dict:
            文档资料类别标识（k）-文档上传结果(v)键值对字典
        :return: 返回新创建的对象的List集合
        """
        doc_list = []
        for tag, results in tag_upload_result_dict.items():
            for (doc_name, path) in results:
                doc, created = self.update_or_create(
                    name=doc_name, category=tag, path=path
                )
                if created:
                    doc.cache()
                    doc_list.append(doc)
        return doc_list

    def bulk_save_or_update_project_doc(self, project_documents):
        """
        批量保存或更新上传的project_document
        :param project_documents:
            文档资料类别list
        :return: 返回新创建的对象的List集合
        """
        try:
            with transaction.atomic():
                doc_list = []
                for project_document in project_documents:
                    doc, is_create = self.update_or_create(
                        name=project_document.get('name'),
                        category=project_document.get('category'),
                        path=project_document.get('path')
                    )
                    if is_create:
                        doc.cache()
                        doc_list.append(doc)
                return doc_list
        except Exception as e:
            logger.exception(e)
            return None


class ProjectMilestoneStateManager(BaseManager):

    def get_project_milestone_state_by_project_milestone(self, project, milestone):
        """
        根据项目和里程碑获取项目里程碑
        """
        return self.filter(project=project, milestone=milestone).first()

    def get_pro_milestone_states_by_id(self, pro_milestone_states_id):
        """
        根据id获取项目里程碑
        """
        return self.filter(pk=pro_milestone_states_id).first()

    def bulk_create_project_milestone_states(self, project, milestones):
        """
        分配负责人成功之后，创建ProjectMilestoneState,绑定项目与流程下里程碑的关系，确定项目的里程碑
        """
        try:
            pro_milestone_states = []
            for milestone in milestones:
                pro_milestone_state = self.model(milestone=milestone, project=project)
                pro_milestone_states.append(pro_milestone_state)
            self.bulk_create(pro_milestone_states)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def get_pro_milestone_states_by_milestone(self, milestone):
        """
        通过流程里程碑获取项目里程碑
        :return:
        """
        return self.filter(milestone=milestone).first()

    def update_project_milestone_state(self, project_milestone_state, **data):
        """
        里程中每个子里程碑下更新当前项目里程碑下保存的数据
        :param project_milestone_state: 更新的项目里程碑
        """
        try:
            project_milestone_state.update(data)
            project_milestone_state.cache()
            return project_milestone_state
        except Exception as e:
            logger.exception(e)
            return None


class SupplierSelectionPlanManager(BaseManager):

    def get_one(self, **data):
        self.filter(data).first()

    def get_list(self, **data):
        self.filter(data)

    def create_plan(self, **data):
        return self.create(self.model(data))

    def bulk_create_plan(self, plan_list):
        return self.bulk_create(plan_list)


class PurchaseContractManager(BaseManager):

    def create_or_update_purchase_contract(self, project_milestone_state=None, contract_devices=None, **data):
        """
        创建采购合同,添加合同采购设备信息
        :param project_milestone_state: 项目里程碑
        :param contract_devices: 合同设备
        """
        try:
            with transaction.atomic():
                purchase_contract = self.filter(project_milestone_state=project_milestone_state).first()
                if not purchase_contract:
                    # 不存在合同的情况下创建合同
                    purchase_contract = self.model(project_milestone_state=project_milestone_state, **data)
                    purchase_contract.save()
                else:
                    # 存在合同的情况下更新合同
                    purchase_contract.update(data)
                # 创建合同设备信息
                contract_device_add_list = []   # 存放待添加的设备
                contract_device_update_list = []  # 存放待更新的设备
                for device_data in contract_devices:
                    if not device_data.get('id'):
                        contract_device_add_list.append(
                            ContractDevice(contract=purchase_contract, **device_data)
                        )
                    else:
                        contract_device_update_list.append(device_data)
                if contract_device_add_list:
                    ContractDevice.objects.bulk_create(contract_device_add_list)
                if contract_device_update_list:
                    # 按照ID升序重新排序
                    contract_device_update_list = sorted(contract_device_update_list, key=lambda item: item['id'])

                    contract_device_id_list = [device['id'] for device in contract_device_update_list]
                    # 获取数据库中相对应的设备集合
                    contract_device_old_list = ContractDevice.objects.filter(pk__in=contract_device_id_list).order_by('id')

                    for index in range(len(contract_device_old_list)):
                        contract_device_old_list[index].name = contract_device_update_list[index].get('name')
                        contract_device_old_list[index].producer = contract_device_update_list[index].get('producer')
                        contract_device_old_list[index].supplier = contract_device_update_list[index].get('supplier')
                        contract_device_old_list[index].real_price = contract_device_update_list[index].get('real_price')
                        contract_device_old_list[index].num = contract_device_update_list[index].get('num')
                        contract_device_old_list[index].real_total_amount = contract_device_update_list[index].get('real_total_amount')
                    # 批量更新
                    helper.bulk_update(contract_device_old_list)
        except Exception as e:
            logger.exception(e)
            return None
        return purchase_contract

    def get_purchase_contract_by_project_milestone_state(self, project_milestone_state):
        """
        通过项目里程碑获取合同信息
        """
        return self.filter(project_milestone_state=project_milestone_state).first()

    def create_purchase_contract(self, project_milestone_state, contract_devices, **data):
        """
        创建采购合同
        """
        try:
            with transaction.atomic():
                purchase_contract = self.model(project_milestone_state=project_milestone_state, **data)
                purchase_contract.save()

                contract_device_list = []
                for contract_device in contract_devices:
                    contract_device_list.append(ContractDevice(contract=purchase_contract, **contract_device))
                ContractDevice.objects.bulk_create(contract_device_list)
        except Exception as e:
            logger.exception(e)
            return None
        return purchase_contract


class ReceiptManager(BaseManager):

    def create_update_receipt(self, project_milestone_state, **data):
        """
        创建或者更新收货单据
        :param project_milestone_state:
        :param data:
        :return:
        """
        try:
            receipt = self.filter(
                project_milestone_state=project_milestone_state).first()
            if not receipt:
                receipt = self.model(project_milestone_state=project_milestone_state, **data)
                receipt.save()
            else:
                receipt.update(data)
        except Exception as e:
            logger.exception(e)
            return None
        return receipt

    def get_receipt_by_project_milestone_state(self, project_milestone_state):

        return self.filter(project_milestone_state=project_milestone_state).first()
