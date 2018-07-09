# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging
from itertools import chain
from base.forms import BaseForm
from nmis.projects.models import ProjectPlan, ProjectFlow
from nmis.projects.consts import PROJECT_STATUS_CHOICES, PROJECT_HANDING_TYPE_CHOICES, \
    PRO_HANDING_TYPE_SELF, PRO_HANDING_TYPE_AGENT
from nmis.hospitals.models import Staff
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
            'devices_empty': '设备列表不能为空或数据错误',
            'device_name_error': '设备名为空或格式错误',
            'device_num_error': '设备购买数量为空或格式错误',
            'device_planned_price_error': '设备预购价格输入错误',
            'err_handing_type': '办理方式为空或数据错误',
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
            self.update_errors('handing_type', 'err_handing_type')
            return False

        if not (handing_type in dict(PROJECT_HANDING_TYPE_CHOICES).keys()):
            self.update_errors('handing_type', 'err_handing_type')
            return False

        return True

    def check_devices(self):
        ordered_devices = self.data.get('ordered_devices')
        if not ordered_devices or len(ordered_devices) == 0:
            self.update_errors('ordered_devices', 'devices_empty')
            return False

        for device in ordered_devices:
            if not device.get('name'):
                self.update_errors('name', 'device_name_error')
                return False

            device_num = device.get('num')
            if not device_num:
                self.update_errors('num', 'device_num_error')
                return False
            try:
                int(device_num)
            except ValueError:
                self.update_errors('num', 'device_num_error')
                return False

            device_planned_price = device.get('planned_price')
            if not device_planned_price:
                self.update_errors('planned_price', 'device_planned_price_error')
                return False
            try:
                float(device_planned_price)
            except ValueError:
                self.update_errors('planned_price', 'device_planned_price_error')
                return False

        return True

    def save(self):
        data = {
            'title': self.data.get('project_title'),
            'handing_type': self.data.get('handing_type'),
            'purpose': self.data.get('purpose'),
            'creator': self.creator,
            'related_dept': self.related_dept,
        }
        if data.get('handing_type') == PRO_HANDING_TYPE_SELF:
            data["performer"] = self.creator

        return ProjectPlan.objects.create_project(self.data.get('ordered_devices'), **data)


class ProjectPlanUpdateForm(BaseForm):
    """
    TODO:添加相关校验
    """

    def __init__(self, old_project, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.old_project = old_project
        self.init_err_codes()
        self.pre_data = self.init_data()

    def init_data(self):
        pre_data = {}
        if self.data.get('project_title', '').strip():
            pre_data['title'] = self.data.get('project_title', '').strip()
        if self.data.get('purpose', '').strip():
            pre_data['purpose'] = self.data.get('purpose', '').strip()
        if self.data.get('handing_type', '').strip():
            pre_data['handing_type'] = self.data.get('handing_type', '').strip()
        if self.data.get('added_devices', []):
            pre_data['added_devices'] = self.data.get('added_devices', [])
        if self.data.get('updated_devices', []):
            pre_data['updated_devices'] = self.data.get('updated_devices', [])
        return pre_data

    def init_err_codes(self):
        self.ERR_CODES.update({
            'project_title_error': '项目名称输入错误',
            'purpose_error': '用途不能为空或数据错误',
            'handing_type_error': '办理方式数据错误'
        })

    def is_valid(self):
        if self.check_project_title() and self.check_devices() and self.check_handing_type():
            return True
        return False

    def check_project_title(self):
        return True

    def check_handing_type(self):
        handing_type = self.pre_data.get('handing_type')
        if not handing_type:
            self.update_errors('handing_type', 'err_handing_type')
            return False

        if not (handing_type in dict(PROJECT_HANDING_TYPE_CHOICES).keys()):
            self.update_errors('handing_type', 'err_handing_type')
            return False

        return True

    def check_devices(self):
        added_devices = self.pre_data.get('added_devices')
        updated_devices = self.pre_data.get('updated_devices')

        if added_devices and len(added_devices) > 0:
            for device in added_devices:
                if not device.get('name'):
                    self.update_errors('name', 'device_name_error')
                    return False

                device_num = device.get('num')
                if not device_num:
                    self.update_errors('num', 'device_num_error')
                    return False
                try:
                    int(device_num)
                except ValueError:
                    self.update_errors('num', 'device_num_error')
                    return False

                device_planned_price = device.get('planned_price')
                if not device_planned_price:
                    self.update_errors('planned_price', 'device_planned_price_error')
                    return False
                try:
                    float(device_planned_price)
                except ValueError:
                    self.update_errors('planned_price', 'device_planned_price_error')
                    return False
        if updated_devices and len(updated_devices) > 0:
            for device in updated_devices:
                if not device.get('name'):
                    self.update_errors('name', 'device_name_error')
                    return False

                device_num = device.get('num')
                if not device_num:
                    self.update_errors('num', 'device_num_error')
                    return False
                try:
                    int(device_num)
                except ValueError:
                    self.update_errors('num', 'device_num_error')
                    return False

                device_planned_price = device.get('planned_price')
                if not device_planned_price:
                    self.update_errors('planned_price', 'device_planned_price_error')
                    return False
                try:
                    float(device_planned_price)
                except ValueError:
                    self.update_errors('planned_price', 'device_planned_price_error')
                    return False
            return True

        return True

    def save(self):
        if not self.old_project.handing_type == self.pre_data['handing_type']:
            if self.pre_data['handing_type'] == PRO_HANDING_TYPE_SELF:
                self.pre_data['performer'] = self.old_project.creator
            if self.pre_data['handing_type'] == PRO_HANDING_TYPE_AGENT:
                self.pre_data['performer'] = None
        return ProjectPlan.objects.update_project(self.old_project, **self.pre_data)


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

