# coding=utf-8
#
# Created by junn, on 2018/6/7
#

#
import logging

from base.forms import BaseForm
from nmis.devices.models import OrderedDevice, SoftwareDevice
from nmis.hospitals.consts import ARCHIVE
from nmis.projects.models import ProjectPlan, ProjectFlow
from nmis.projects.consts import PROJECT_STATUS_CHOICES, PROJECT_HANDING_TYPE_CHOICES, \
    PRO_HANDING_TYPE_SELF, PRO_HANDING_TYPE_AGENT, PRO_CATE_HARDWARE, PRO_CATE_SOFTWARE, \
    PROJECT_DOCUMENT_CATE_CHOICES, PROJECT_DOCUMENT_DIR
from nmis.hospitals.models import Staff
from utils import eggs
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
            'project_title_error': '项目名称输入错误',
            'handing_type_error': '办理方式为空或数据错误',
            'software_name_error': '软件名称为空或数据错误',
            'software_purpose_error': '软件用途为空或数据错误',
            'hardware_devices_error': '硬件设备为空或格式错误',
            'software_devices_error': '软件设备为空或格式错误',
            'devices_error': '硬件设备和软件设备不可同时为空'
        })

    def is_valid(self):
        return self.check_project_title() and self.check_devices() and self.check_handing_type()

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

            # 信息化项目存在硬件设备申请需对硬件设备字段进行校验
            if self.data.get('hardware_devices'):
                return check_hardware_devices_list(self, self.data.get('hardware_devices'))

            # 信息化项目存在软件设备申请需对软件设备字段进行校验
            if software_devices:
                for item in software_devices:
                    if not item.get('name'):
                        self.update_errors('software_name', 'software_name_error')
                        return False
                    if not item.get('purpose'):
                        self.update_errors('software_purpose', 'software_purpose_error')
                        return False
            if not software_devices and not self.data.get('hardware_devices'):
                self.update_errors('devices', 'devices_error')
                return False

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
            'pre_amount': self.data.get('pre_amount')
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
            'project_title_error': '项目名称输入错误',
            'purpose_error': '用途不能为空或数据错误',
            'handing_type_error': '办理方式数据错误',
            'software_name_error': '软件名称为空或数据错误',
            'software_purpose_error': '软件用途为空或数据错误',
            'software_id_error': '更新设备ID不存在'
        })

    def is_valid(self):
        if self.check_project_title() and self.check_devices() and self.check_handing_type():
            return True
        return False

    def check_project_title(self):
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
        return True

    def save(self):

        pro_data = {}
        if self.data.get('project_title'):
            pro_data['title'] = self.data.get('project_title').strip()

        if self.data.get('purpose'):
            pro_data['purpose'] = self.data.get('purpose').strip()

        if self.data.get('project_introduce'):
            pro_data['project_introduce'] = self.data.get('project_introduce').strip()

        if self.data.get('handing_type'):
            pro_data['handing_type'] = self.data.get('handing_type').strip()

        if self.data.get('hardware_added_devices'):
            pro_data['hardware_added_devices'] = self.data.get('hardware_added_devices')

        if self.data.get('hardware_updated_devices'):
            pro_data['hardware_updated_devices'] = self.data.get(
                'hardware_updated_devices')

        if self.data.get('software_added_devices'):
            pro_data['software_added_devices'] = self.data.get('software_added_devices')

        if self.data.get('software_updated_devices'):
            pro_data['software_updated_devices'] = self.data.get(
                'software_updated_devices')

        if self.data.get('handing_type') == PRO_HANDING_TYPE_SELF:
            self.old_project.performer = self.old_project.creator
        if self.data.get('handing_type') == PRO_HANDING_TYPE_AGENT:
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
        'devices_empty': '设备列表不能为空或数据错误',
        'device_name_error': '设备名为空或格式错误',
        'device_num_error': '设备购买数量为空或格式错误',
        'device_planned_price_error': '设备预购价格输入错误',
        'device_measure_error': '设备度量单位为空或数据错误',
        'device_type_spec_error': '设备规格/型号为空或数据错误',
        'device_purpose_error': '设备用途数据错误',
        'updated_device_not_exist': '更新的设备不存在',
        'updated_device_id_error': '更新的设备ID数据错误',
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
                result = upload_file(file, PROJECT_DOCUMENT_DIR+str(self.project_id)+'/', file.name)
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

        for tag in self.req.FILES.keys():
            file = self.req.FILES.get(tag)
            result = single_upload_file(file, PROJECT_DOCUMENT_DIR + str(self.project_id) + '/',
                                 file.name)
            if not result:
                return '%s%s' % (file.name, '上传失败'), False

            return result, file.name, True


class PurchaseContractCreateForm(BaseForm):

    def __init__(self, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.data = data

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'seller_tel_err': '乙方电话错误',
            'device_num_err': '设备数量错误',
            'device_name_err': '设备名称错误',
            'device_measure': '设备单位错误',
            'device_producer_err': '设备生产商错误',
            'device_amount_err': '设备总价错误',
            'device_supplier_err': '供应商错误'
        })

    def is_valid(self):
        if not self.check_seller_tel() or not self.check_device():
            return False
        return True

    def check_device(self):
        """
        校验设备数量
        """
        contract_device_list = self.data.get('contract_device')
        for device in contract_device_list:
            print(device)
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
            if not device.get('measure', '').strip():
                self.update_errors('device_measure', 'device_measure_err')
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
        contract_data = {}
        if self.data.get('contract_no', ).strip():
            contract_data['contract_no'] = self.data.get('contract_no', ).strip()
        if self.data.get('title', ).strip():
            contract_data['title'] = self.data.get('title', ).strip()
        if self.data.get('signed_date', ).strip():
            contract_data['signed_date'] = self.data.get('signed_date', ).strip()
        if self.data.get('buyer_contact', ).strip():
            contract_data['buyer_contact'] = self.data.get('buyer_contact', ).strip()
        if self.data.get('seller_contact', ).strip():
            contract_data['seller_contact'] = self.data.get('seller_contact', ).strip()
        if self.data.get('seller', ).strip():
            contract_data['seller'] = self.data.get('seller', ).strip()
        if self.data.get('seller_tel', ).strip():
            contract_data['seller_tel'] = self.data.get('seller_tel', ).strip()
        if self.data.get('total_amount', ).strip():
            contract_data['total_amount'] = self.data.get('total_amount', ).strip()
        if self.data.get('delivery_date', ).strip():
            contract_data['delivery_date'] = self.data.get('delivery_date', ).strip()

        pass
