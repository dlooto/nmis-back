# coding=utf-8
#
# Created by junn, on 2018/6/7
#

#
import logging
import time

from base.forms import BaseForm
from nmis.devices.models import OrderedDevice, SoftwareDevice
from nmis.hospitals.consts import ARCHIVE
from nmis.projects.models import ProjectPlan, ProjectFlow, ProjectDocument, \
    PurchaseContract, ProjectMilestoneState, SupplierSelectionPlan, Supplier, Receipt
from nmis.projects.consts import PROJECT_STATUS_CHOICES, PROJECT_HANDING_TYPE_CHOICES, \
    PRO_HANDING_TYPE_SELF, PRO_HANDING_TYPE_AGENT, PRO_CATE_HARDWARE, PRO_CATE_SOFTWARE, \
    PROJECT_DOCUMENT_CATE_CHOICES, PROJECT_DOCUMENT_DIR, PROJECT_PURCHASE_METHOD_CHOICES, PRO_DOC_CATE_OTHERS, \
    PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN, PRO_DOC_CATE_PLAN_ARGUMENT
from nmis.hospitals.models import Staff
from utils import eggs, times
from utils.files import upload_file, single_upload_file

logs = logging.getLogger(__name__)


class ProjectPlanCreateForm(BaseForm):
    """
    创建项目申请表单
    """
    def __init__(self, creator, related_dept, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.creator = creator
        self.related_dept = related_dept

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'project_title_error':              '项目名称输入错误',
            'handing_type_error':               '办理方式为空或数据错误',
            'software_name_error':              '软件名称为空或数据错误',
            'software_purpose_error':           '软件用途为空或数据错误',
            'hardware_devices_error':           '硬件设备为空或格式错误',
            'software_devices_error':           '软件设备为空或格式错误',
            'devices_error':                    '硬件设备和软件设备不可同时为空',
            'planned_price_null_err':           '软件预估单价为空',
            'planned_price_format_err':         '软件预估单价数据类型错误',
            'pre_amount_null_err':              '项目总价为空',
            'pre_amount_format_err':            '项目总价数据类型错误'
        })

    def is_valid(self):
        return self.check_project_title() and self.check_devices() and\
               self.check_handing_type() and self.check_pre_amount()

    def check_pre_amount(self):

        if not self.data.get('pre_amount'):
            self.update_errors('pre_amount', 'pre_amount_null_err')
            return False
        try:
            if not isinstance(float(self.data.get('pre_amount')), float):
                self.update_errors('pre_amount', 'pre_amount_format_err')
                return False
        except ValueError:
            self.update_errors('pre_amount', 'pre_amount_format_err')
            return False
        return True

    def check_project_title(self):
        project_title = self.data.get('project_title')
        if not project_title:
            self.update_errors('project_title', 'project_title_error')
            return False
        return True

    def check_handing_type(self):
        handing_type = self.data.get('handing_type')
        if not handing_type:
            self.update_errors('handing_type', 'handing_type_error')
            return False

        if not (handing_type in dict(PROJECT_HANDING_TYPE_CHOICES).keys()):
            self.update_errors('handing_type', 'handing_type_error')
            return False

        return True

    def check_devices(self):
        pro_type = self.data.get('pro_type')
        if pro_type == PRO_CATE_HARDWARE:
            # 新建医疗器械设备字段进行校验
            if not self.data.get('hardware_devices'):
                self.update_errors('hardware_devices', 'hardware_devices_error')
                return False
            return check_hardware_devices_list(self, self.data.get('hardware_devices'))
        else:
            # 信息化项目设备校验
            software_devices = self.data.get('software_devices')        # 信息化项目软件设备
            if not software_devices and not self.data.get('hardware_devices'):
                self.update_errors('devices', 'devices_error')
                return False
            # 信息化项目存在软件设备申请需对软件设备字段进行校验
            if software_devices:
                for item in software_devices:
                    if not item.get('name'):
                        self.update_errors('software_name', 'software_name_error')
                        return False
                    if not item.get('purpose'):
                        self.update_errors('software_purpose', 'software_purpose_error')
                        return False
                    if not item.get('planned_price'):
                        self.update_errors('planned_price', 'planned_price_null_err')
                        return False

                    try:
                        if not isinstance(float(item.get('planned_price')), float):
                            self.update_errors('planned_price', 'planned_price_format_err')
                            return False
                    except ValueError:
                        self.update_errors('planned_price', 'planned_price_format_err')
                        return False
            # 信息化项目存在硬件设备申请需对硬件设备字段进行校验
            if self.data.get('hardware_devices'):
                return check_hardware_devices_list(self, self.data.get('hardware_devices'))
        return True

    def save(self):
        data = {
            'title': self.data.get('project_title'),
            'handing_type': self.data.get('handing_type'),
            'purpose': self.data.get('purpose'),
            'creator': self.creator,
            'related_dept': self.related_dept,
            'project_cate': self.data.get('pro_type'),
            'project_introduce': self.data.get('project_introduce'),
            'pre_amount': float(self.data.get('pre_amount'))
        }
        if data.get('handing_type') == PRO_HANDING_TYPE_SELF:
            data["performer"] = self.creator

        return ProjectPlan.objects.create_project(
            software_devices=self.data.get('software_devices'),     # 软件设备明细
            hardware_devices=self.data.get('hardware_devices'),     # 硬件设备明细
            **data                                                  # 新建项目属性列表
        )


class ProjectPlanUpdateForm(BaseForm):
    """
    TODO:添加相关校验
    """

    def __init__(self, old_project, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.old_project = old_project
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'project_title_error':      '项目名称输入错误',
            'purpose_error':            '用途不能为空或数据错误',
            'handing_type_error':       '办理方式数据错误',
            'software_name_error':      '软件名称为空或数据错误',
            'software_purpose_error':   '软件用途为空或数据错误',
            'software_id_error':        '更新设备ID不存在',
            'pre_amount_err':           '项目总价错误',
            'planned_price_null_err':   '软件预估单价为空',
            'planned_price_format_err': '软件预估单价数据类型错误',
            'pre_amount_null_err':      '项目总价为空',
            'pre_amount_format_err':    '项目总价数据类型错误'
        })

    def is_valid(self):
        if self.check_project_title() and self.check_devices()\
                and self.check_handing_type() and self.check_pre_amount():
            return True
        return False

    def check_pre_amount(self):
        if self.data.get('pre_amount'):
            try:
                if not isinstance(float(self.data.get('pre_amount')), float):
                    self.update_errors('pre_amount', 'pre_amount_format_err')
                    return False
            except ValueError:
                self.update_errors('pre_amount', 'pre_amount_format_err')
                return False
        return True

    def check_project_title(self):
        return True

    def check_handing_type(self):
        handing_type = self.data.get('handing_type')
        if not handing_type:
            self.update_errors('handing_type', 'handing_type_error')
            return False

        if handing_type not in dict(PROJECT_HANDING_TYPE_CHOICES):
            self.update_errors('handing_type', 'handing_type_error')
            return False

        return True

    def check_devices(self):
        hardware_added_devices = self.data.get('hardware_added_devices')
        hardware_updated_devices = self.data.get('hardware_updated_devices')

        if hardware_added_devices:
            if not check_hardware_devices_list(self, hardware_added_devices):
                return False

        if hardware_updated_devices:
            if not check_hardware_devices_list(self, hardware_updated_devices):
                return False
        # 信息化项目校验
        if self.old_project.project_cate == PRO_CATE_SOFTWARE:
            software_added_devices = self.data.get('software_added_devices')
            software_updated_devices = self.data.get('software_updated_devices')

            if software_added_devices:
                for device in software_added_devices:
                    if not device.get('name'):
                        self.update_errors('software_name', 'software_name_error')
                        return False
                    if not device.get('purpose'):
                        self.update_errors('software_purpose', 'software_purpose_error')
                        return False
                    if not device.get('planned_price'):
                        self.update_errors('planned_price', 'planned_price_null_err')
                        return False

                    try:
                        if not isinstance(float(device.get('planned_price')), float):
                            self.update_errors('planned_price', 'planned_price_format_err')
                            return False
                    except ValueError:
                        self.update_errors('planned_price', 'planned_price_format_err')
                        return False
            if software_updated_devices:
                for device in software_updated_devices:
                    software = SoftwareDevice.objects.filter(id=device.get('id'))[0]
                    if not software:
                        self.update_errors('software_id', 'software_id_error')
                        return False
                    if not device.get('name'):
                        self.update_errors('software_name', 'software_name_error')
                        return False
                    if not device.get('purpose'):
                        self.update_errors('software_purpose', 'software_purpose_error')
                        return False

                    if not device.get('planned_price'):
                        self.update_errors('planned_price', 'planned_price_null_err')
                        return False

                    try:
                        if not isinstance(float(device.get('planned_price')), float):
                            self.update_errors('planned_price', 'planned_price_format_err')
                            return False
                    except ValueError:
                        self.update_errors('planned_price', 'planned_price_format_err')
                        return False

        return True

    def save(self):
        pro_data = {}
        if self.data.get('project_title', '').strip():
            pro_data['title'] = self.data.get('project_title').strip()

        if self.data.get('purpose', '').strip():
            pro_data['purpose'] = self.data.get('purpose').strip()

        if self.data.get('project_introduce', '').strip():
            pro_data['project_introduce'] = self.data.get('project_introduce').strip()

        if self.data.get('handing_type', '').strip():
            pro_data['handing_type'] = self.data.get('handing_type').strip()

        if self.data.get('hardware_added_devices'):
            pro_data['hardware_added_devices'] = self.data.get('hardware_added_devices')

        if self.data.get('hardware_updated_devices'):
            pro_data['hardware_updated_devices'] = self.data.get(
                'hardware_updated_devices')

        if self.data.get('software_added_devices'):
            pro_data['software_added_devices'] = self.data.get('software_added_devices')

        if self.data.get('software_updated_devices'):
            pro_data['software_updated_devices'] = self.data.get('software_updated_devices')

        if self.data.get('handing_type', '').strip() == PRO_HANDING_TYPE_SELF:
            self.old_project.performer = self.old_project.creator
        if self.data.get('handing_type', '').strip() == PRO_HANDING_TYPE_AGENT:
            self.old_project.performer = None

        return ProjectPlan.objects.update_project(self.old_project, **pro_data)


def check_hardware_devices_list(baseForm, devices_list):
    """
    校验设备信息

    :param baseForm: BaseForm类及其子类实例对象
    :param devices_list: 设备List ，list中的元素由设备属性作作为键的dict
    :return: True/False
    """
    baseForm.ERR_CODES.update({
        'devices_empty': '硬件设备列表不能为空或数据错误',
        'device_name_error': '硬件设备名为空或格式错误',
        'device_num_error': '硬件设备购买数量为空或格式错误',
        'device_planned_price_error': '硬件设备预购价格数据类型错误',
        'device_measure_error': '硬件设备度量单位为空或数据错误',
        'device_type_spec_error': '硬件设备规格/型号为空或数据错误',
        'device_purpose_error': '硬件设备用途数据错误',
        'updated_device_not_exist': '硬件更新的设备不存在',
        'updated_device_id_error': '硬件更新的设备ID数据错误',
    })
    for device in devices_list:
        device_id = device.get('id')
        if device_id:
            try:
                int(device_id)
                order_device = OrderedDevice.objects.filter(id=device_id)
                if not order_device:
                    baseForm.update_errors('num', 'updated_device_not_exist')
                    return False
            except ValueError:
                baseForm.update_errors('num', 'updated_device_id_error')
                return False

        if not device.get('name', '').strip():
            baseForm.update_errors('name', 'device_name_error')
            return False

        device_num = device.get('num')
        if not device_num:
            baseForm.update_errors('num', 'device_num_error')
            return False

        try:
            int(device_num)
            if isinstance(device_num, float):
                baseForm.update_errors('num', 'device_num_error')
                return False
        except ValueError:
            baseForm.update_errors('num', 'device_num_error')
            return False

        device_planned_price = device.get('planned_price')
        if not device_planned_price:
            baseForm.update_errors('planned_price', 'device_planned_price_error')
            return False
        try:
            float(device_planned_price)
        except ValueError:
            baseForm.update_errors('planned_price', 'device_planned_price_error')
            return False

        if not device.get('measure', '').strip():
            baseForm.update_errors('measure', 'device_measure_error')
            return False

        if not device.get('type_spec', '').strip():
            baseForm.update_errors('type_spec', 'device_type_spec_error')
            return False
        if not device.get('purpose', '').strip():
            pass
    return True


class BaseOrderedDeviceForm(BaseForm):

    def __init__(self, project, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.project = project

    def is_valid(self):
        return True

    def save(self):
        pass


class OrderedDeviceCreateForm(BaseOrderedDeviceForm):

    def save(self):
        data = {
            "name": self.data.get("name", '').strip(),
            "planned_price": self.data.get("planned_price"),
            "num": self.data.get("num"),
            "type_spec": self.data.get("type_spec", '').strip(),
            "measure": self.data.get("measure", "").strip(),
            "purpose": self.data.get("purpose", '').strip(),
        }
        return self.project.create_device(**data)


class OrderedDeviceUpdateForm(BaseOrderedDeviceForm):

    def __init__(self, device, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.device = device

    def save(self):
        data = {
            "name": self.data.get('name').strip(),
            "num": self.data.get("num"),
        }
        if self.data.get('name', ''):
            data["name"] = self.data.get('name', '').strip()
        if self.data.get('num'):
            data["num"] = self.data.get('num')
        if self.data.get('planned_price'):
            data["planned_price"] = self.data.get('planned_price')
        if self.data.get('purpose'):
            data["purpose"] = self.data.get('purpose', '').strip()
        if self.data.get('type_spec'):
            data["type_spec"] = self.data.get('type_spec', '').strip()

        self.device.update(data)
        return self.device


class ProjectFlowCreateForm(BaseForm):

    def __init__(self, organ, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.organ = organ

        self.ERR_CODES.update({
            "err_flow_title":       "流程标题错误",
            "err_milestone_title":  "里程碑项标题错误",
        })

    def is_valid(self):
        return True

    def check_flow_title(self):
        title = self.data.get('flow_title', '').strip()
        if not title:
            self.update_errors('flow_title', 'err_flow_title')
            return False
        return True

    def check_milestones(self):
        milestones = self.data.get("milestones")
        return True

    def save(self):
        data = {
            "title": self.data.get("flow_title", '').strip(),
            "organ": self.organ,
        }

        return ProjectFlow.objects.create_flow(self.data.get("milestones"), **data)


class ProjectFlowUpdateForm(BaseForm):

    def __init__(self, old_flow, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, kwargs)
        self.old_flow = old_flow

        self.ERR_CODES.update({
            "flow_is_used":     "流程已经在使用中，不能修改",
            "err_flow_title":   "流程标题错误",
        })

    def is_valid(self):
        if not self.check_flow_used():
            return False
        if not self.check_flow_title():
            return False
        return True

    def check_flow_title(self):
        title = self.data.get('flow_title', '').strip()
        if not title:
            self.update_errors('flow_title', 'err_flow_title')
            return False
        return True

    def check_flow_used(self):
        if self.old_flow.is_used():
            self.update_errors('flow_id', 'flow_is_used')
            return False
        return True

    def save(self):
        data = {
            'title': self.data.get('flow_title', '').strip(),
        }
        new_flow = self.old_flow.update(data)
        new_flow.cache()
        return new_flow


class ProjectPlanListForm(BaseForm):
    def __init__(self, req, hospital, *args, **kwargs):
        BaseForm.__init__(self, req, hospital, *args, **kwargs)

        self.req = req
        self.hospital = hospital

        self.ERR_CODES.update({
            "err_status": "项目状态异常"
        })

    def is_valid(self):
        return self.check_status()

    def check_status(self):
        status = self.req.GET.get('pro_status')

        # 项目状态不为必须传入参数，如果为None时直接返回Ture
        if not status:
            return True

        # 判断项目状态status是否存在PROJECT_STATUS_CHOICES，不存在返回False
        if not status in dict(PROJECT_STATUS_CHOICES).keys():
            self.update_errors('status', 'err_status')
            return False
        return True

    def my_projects(self):

        data = {}

        if self.req.GET.get('pro_status', ''):
            data['status'] = self.req.GET.get('pro_status', '').strip()

        # 判断是否存在项目名和项目负责人关键字
        performers = None
        search_key = self.req.GET.get('search_key', '').strip()
        if search_key:
            performers = Staff.objects.get_by_name(self.hospital, search_key)

        return ProjectPlan.objects.get_by_search_key(
            self.hospital, project_title=search_key, performers=performers, **data
        )


class UploadFileForm(BaseForm):

    def __init__(self, req, project_id, *args, **kwargs):
        BaseForm.__init__(self, req, project_id, *args, **kwargs)
        self.req = req
        self.project_id = project_id

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_type_err': '文件类型错误',
            'file_key_err': 'key类型错误'
        })

    def is_valid(self):
        if not self.check_file_type() or not self.check_file_key():
            return False
        return True

    def check_file_type(self):
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                if file.content_type not in ARCHIVE.values():
                    self.update_errors('%s' % file.name, 'file_type_err')
                    return False
        return True

    def check_file_key(self):
        for tag in self.req.FILES.keys():
            if tag not in dict(PROJECT_DOCUMENT_CATE_CHOICES):
                self.update_errors('file_key', 'file_key_err')
                return False
        return True

    def save(self):
        file_name_path_data = {}

        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            result_files = []
            for file in files:
                result = upload_file(file, PROJECT_DOCUMENT_DIR+str(self.project_id)+'/')
                print(result)
                if not result:
                    return '%s%s' % (file.name, '上传失败'), False

                result_files.append(result)
                file_name_path_data[tag] = result_files

        return file_name_path_data, True


class SingleUploadFileForm(BaseForm):

    def __init__(self, req, project_id, *args, **kwargs):
        BaseForm.__init__(self, req, project_id, *args, **kwargs)
        self.req = req
        self.project_id = project_id

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_type_err': '不支持的文件类型',
            'file_key_err': 'key值为空',
            'file_name_err': '文件名称错误',
            'file_size_err': '上传文件过大，默认上传大小2.5M'
        })

    def is_valid(self):
        if not self.check_file_type() or not self.check_file_size() or not self.check_file_key():
            return False
        return True

    def check_file_type(self):
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                if file.content_type not in ARCHIVE.values():
                    self.update_errors('%s' % file.name, 'file_type_err')
                    return False
        return True

    def check_file_name(self):
        pass

    def check_file_key(self):
        if not self.req.FILES.keys():
            self.update_errors('file_key', 'file_key_err')
            return False
        # for tag in self.req.FILES.keys():
        #     if tag not in dict(PROJECT_DOCUMENT_CATE_CHOICES):
        #         self.update_errors('file_key', 'file_key_err')
        #         return False
        return True

    def check_file_size(self):
        """
        校验文件大小，以字节校验，默认2621440字节（2.5M）
        :return:
        """
        for tag in self.req.FILES.keys():
            file = self.req.FILES.get(tag)
            if file.size > 2621440:
                self.update_errors('file_size', 'file_size_err')
                return False
        return True

    def save(self):
        for tag in self.req.FILES.keys():
            file = self.req.FILES.get(tag)
            result = single_upload_file(file, PROJECT_DOCUMENT_DIR + str(self.project_id) + '/',
                                        file.name)
            if not result:
                return '%s%s' % (file.name, '上传失败'), False

            return result, file.name, True


class ProjectDocumentBulkCreateOrUpdateForm(BaseForm):

    def __init__(self, documents, *args, **kwargs):
        BaseForm.__init__(self, documents, *args, **kwargs)
        self.documents = documents

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_category_err': '文档类型错误',
        })

    def is_valid(self):
        if not self.check_file_category():
            return False
        return True

    def check_file_category(self):
        if self.documents:
            for document in self.documents:
                if document.get('category') not in dict(PROJECT_DOCUMENT_CATE_CHOICES):
                    self.update_errors('file_category', 'file_category_err')
                    return False
        return True

    def save(self):
        project_documents = []
        if self.documents:
            for document in self.documents:
                if document.get('files'):
                    for file in document.get('files'):
                        project_document = {
                            'category': document.get('category'),
                            'path': file.get('path'),
                            'name': file.get('name')
                        }
                        project_documents.append(project_document)
        return ProjectDocument.objects.bulk_save_or_update_project_doc(
            project_documents) if project_documents else None


class PurchaseContractCreateForm(BaseForm):

    def __init__(self, pro_milestone_state, data, *args, **kwargs):
        BaseForm.__init__(self, pro_milestone_state, data, *args, **kwargs)

        self.project_milestone_state = pro_milestone_state
        self.data = data
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'seller_tel_err': '乙方电话错误',
            'device_num_err': '设备数量错误',
            'device_name_err': '设备名称错误',
            'device_producer_err': '设备生产商错误',
            'device_amount_err': '设备总价错误',
            'device_supplier_err': '供应商错误',
        })

    def is_valid(self):
        if not self.check_seller_tel() or not self.check_device():
            return False
        return True

    def check_device(self):
        """
        校验设备信息
        """
        contract_device_list = self.data.get('contract_devices')
        for device in contract_device_list:
            if not device.get('num'):
                self.update_errors('device_num', 'device_num_err')
                return False
            else:
                if not isinstance(device.get('num'), int):
                    self.update_errors('device_num', 'device_num_err')
                    return False

            if not device.get('name', '').strip():
                self.update_errors('device_name', 'device_name_err')
                return False
            if not device.get('supplier', '').strip():
                self.update_errors('device_supplier', 'device_supplier_err')
                return False
            if not device.get('real_total_amount'):
                self.update_errors('device_amount', 'device_amount_err')
                return False
            else:
                if not isinstance(device.get('real_total_amount'), float)\
                        and not isinstance(device.get('real_total_amount'), int):
                    self.update_errors('device_amount', 'device_amount_err')
                    return False

            if not device.get('producer', '').strip():
                self.update_errors('device_producer', 'device_producer_err')
                return False
        return True

    def check_seller_tel(self):
        """
        校验乙方联系人手机号
        """
        contact_phone = self.data.get('seller_tel', '').strip()
        if not eggs.is_phone_valid(contact_phone):
            self.update_errors('seller_tel', 'seller_tel_err')
            return False
        return True

    def save(self):
        contract_data = {
            'contract_no': self.data.get('contract_no', '').strip(),
            'title': self.data.get('title', '').strip(),
            'signed_date': self.data.get('signed_date', '').strip(),
            'buyer_contact': self.data.get('buyer_contact', '').strip(),
            'seller_contact': self.data.get('seller_contact', '').strip(),
            'seller': self.data.get('seller', '').strip(),
            'seller_tel': self.data.get('seller_tel', '').strip(),
            'total_amount': self.data.get('total_amount'),
            'delivery_date': self.data.get('delivery_date', '').strip(),
        }

        return PurchaseContract.objects.create_or_update_purchase_contract(
                project_milestone_state=self.project_milestone_state,
                contract_devices=self.data.get('contract_devices'), **contract_data)


class ProjectMilestoneStateUpdateForm(BaseForm):
    """
    更新ProjectMilestoneState
    """
    def __init__(self, doc_list, old_doc_list, summary, project_milestone_state, user_profile, project, *args, **kwargs):
        BaseForm.__init__(self, doc_list, old_doc_list, summary, project_milestone_state, user_profile, project, *args, **kwargs)
        self.project = project
        self.project_milestone_state = project_milestone_state
        self.doc_list = doc_list
        self.old_doc_list = project_milestone_state.doc_list
        self.user_profile = user_profile
        self.summary = summary

    def init_err_codes(self):
        self.ERR_CODES.update({
        })

    def is_valid(self):
        pass

    def save(self):
        pro_milestone_state_data = {}
        if self.doc_list:
            doc_ids_str = ','.join('%s' % doc.id for doc in self.doc_list)
            if not self.old_doc_list:
                pro_milestone_state_data['doc_list'] = doc_ids_str
            else:
                pro_milestone_state_data['doc_list'] = '%s%s%s' % (self.old_doc_list, ',', doc_ids_str)

        if self.summary:
            if self.user_profile == self.project.performer:
                if self.summary:
                    pro_milestone_state_data['summary'] = self.summary.strip()
        pro_milestone_state_data['modified_time'] = times.now()
        return ProjectMilestoneState.objects.update_project_milestone_state(
            self.project_milestone_state, **pro_milestone_state_data
        ) if pro_milestone_state_data else self.project_milestone_state


class SupplierSelectionPlanBatchSaveForm(BaseForm):

    def __init__(self, pro_milestone_state, data, *args, **kwargs):
        BaseForm.__init__(self, pro_milestone_state, data, *args, **kwargs)

        self.project_milestone_state = pro_milestone_state
        self.data = data
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'plan_list_err': 'plan_list为空或数据异常',
            'id_err': 'id数据异常',
            'supplier_name_err': '供应商名称为空或数据异常',
            'total_amount_err': '方案总价为空数据异常',
            'remark_err': '备注数据异常',
            'plan_files_err': '方案附件不能为空',
            'file_name_err': '文档名称为空或数据异常',
            'file_path_err': '文档路径为空或数据异常',

        })

    def is_valid(self):
        if not self.check_plan_list() or not self.check_plan() or not self.check_supplier_name()\
                or not self.check_total_amount() or not self.check_files():
            return False

        return True

    def check_plan_list(self):
        if not self.data.get('plan_list'):
            self.update_errors('plan_list', 'plan_list_err')
            return False
        return True

    def check_plan(self):
        for plan in self.data.get('plan_list'):
            if not plan.get('id'):
                continue
            try:
                int(plan.get('id'))
            except ValueError as e:
                logs.exception(e)
                self.update_errors('id', 'id_err')
                return False
            if not SupplierSelectionPlan.objects.filter(id=int(plan.get('id'))).first():
                self.update_errors('id', 'id_err')
                return False
        return True

    def check_supplier_name(self):
        plan_list = self.data.get('plan_list')
        for plan in plan_list:
            if not plan.get("supplier_name"):
                self.update_errors('supplier_name', 'supplier_name_err')
                return False
        return True

    def check_total_amount(self):
        plan_list = self.data.get('plan_list')
        for plan in plan_list:
            total_amount = plan.get('total_amount')
            if not total_amount:
                self.update_errors('total_amount', 'total_amount_err')
                return False
            try:
                float(total_amount)
            except ValueError as e:
                logs.exception(e)
                self.update_errors('total_amount', 'total_amount_err')
                return False
        return True

    def check_remark(self):
        # plan_list = self.data.get('plan_list')
        # for plan in plan_list:
        #     if plan.get('remark') is not None:
        #         self.update_errors('remark', 'remark_err')
        #         return False
        return True

    def check_files(self):
        plan_list = self.data.get('plan_list')
        for plan in plan_list:
            plan_files = plan.get('plan_files')
            if not plan_files:
                self.update_errors('plan_files', 'plan_files_err')
                return False
            if plan_files:
                for file in plan_files:
                    if not file.get('name'):
                        self.update_errors('name', 'file_name_err')
                        return False
                    if not file.get('path'):
                        self.update_errors('path', 'file_path_err')
            other_files = plan.get('other_files')
            if other_files:
                for file in other_files:
                    if not file.get('name'):
                        self.update_errors('name', 'file_name_err')
                        return False
                    if not file.get('path'):
                        self.update_errors('path', 'file_path_err')
        return True

    def pre_handle_file_data(self, plan_files, other_files):

        if not plan_files and other_files:
            return None
        file_dict_list = []
        if plan_files:
            for file in plan_files:
                file_dict = {
                    'category': PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN,
                    'path': file.get('path'),
                    'name': file.get('name')
                }
                file_dict_list.append(file_dict)
        if other_files:
            for file in other_files:
                file_dict = {
                    'category': PRO_DOC_CATE_OTHERS,
                    'path': file.get('path'),
                    'name': file.get('name')
                }
                file_dict_list.append(file_dict)
        return self.batch_update_or_create_document(file_dict_list)

    def batch_update_or_create_document(self, file_dict_list):
        document_dict = {
            'updated': [],
            'created': [],
            'all': [],
        }
        if not file_dict_list:
            return document_dict
        try:
            for file_dict in file_dict_list:
                document, created = ProjectDocument.objects.update_or_create(**file_dict)
                document_dict['all'].append(document)
                if created:
                    document_dict['created'].append(document)
                else:
                    updated_doc = ProjectDocument.objects.filter(**file_dict).first()
                    document_dict['updated'].append(updated_doc)
            return document_dict
        except Exception as e:
            logs.exception(e)
            raise e

    def save(self):
        plan_param_list = self.data.get('plan_list')
        try:
            for item in plan_param_list:
                plan_data = dict()
                supplier_name = item.get('supplier_name').strip()
                supplier, created = Supplier.objects.update_or_create(name=supplier_name)
                supplier.cache()
                plan_data['supplier'] = supplier
                plan_data['total_amount'] = float(item.get('total_amount'))
                if item.get('remark') is not None:
                    plan_data['remark'] = item.get('remark').strip()
                plan_file_paths = item.get('plan_files')
                other_file_paths = item.get('other_files')
                document_dict = self.pre_handle_file_data(plan_file_paths, other_file_paths)
                new_doc_list = document_dict.get('all')
                if not new_doc_list:
                    plan_data['doc_list'] = ''
                else:
                    doc_ids_str = ','.join('%s' % doc.id for doc in new_doc_list)
                    plan_data['doc_list'] = doc_ids_str
                if item.get('id') and int(item.get('id')) > 0:
                    plan = SupplierSelectionPlan.objects.filter(id=int(item.get('id'))).first()
                    if plan:
                        plan.update(plan_data)
                        plan.cache()
                else:

                    plan = SupplierSelectionPlan.objects.create(project_milestone_state=self.project_milestone_state, **plan_data)
                    plan.cache()

            return self.project_milestone_state
        except Exception as e:
            logs.exception(e)
            raise e


class ReceiptCreateOrUpdateForm(BaseForm):

    def __init__(self, data, project_milestone_state, *args, **kwargs):
        BaseForm.__init__(self, data, project_milestone_state, *args, **kwargs)
        self.project_milestone_state = project_milestone_state

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'contact_phone_err': '乙方电话错误',
        })

    def is_valid(self):
        if not self.check_contact_phone():
            return False
        return True

    def check_contact_phone(self):
        contact_phone = self.data.get('contact_phone', '').strip()
        if not eggs.is_phone_valid(contact_phone):
            self.update_errors('contact_phone', 'contact_phone_err')
            return False
        return True

    def save(self):
        delivery_data = {
            'served_date': self.data.get('served_date', '').strip(),
            'delivery_man': self.data.get('delivery_man', '').strip(),
            'contact_phone': self.data.get('contact_phone', '').strip()
        }

        return Receipt.objects.create_update_receipt(self.project_milestone_state, **delivery_data)