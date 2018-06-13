# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from base.forms import BaseForm
from nmis.projects.models import ProjectPlan

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
        })

    def is_valid(self):
        return self.check_project_title() and self.check_devices()

    def check_project_title(self):
        project_title = self.data.get('project_title')
        if not project_title:
            self.update_errors('project_title', 'project_title_error')
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
            'purpose': self.data.get('purpose'),
            'creator': self.creator,
            'related_dept': self.related_dept,
        }
        return ProjectPlan.objects.create_project(self.data.get('ordered_devices'), **data)


class ProjectPlanUpdateForm(ProjectPlanCreateForm):

    def __init__(self, old_project, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.old_project = old_project
        self.init_err_codes()

    def save(self):
        data = {
            'title': self.data.get('project_title'),
            'purpose': self.data.get('purpose'),
            'ordered_devices': self.data.get('ordered_devices')
        }
        return self.old_project.update(data)


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
            "purpose": self.data.get("purpose", '').strip()
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

        self.device.update(data)
        return self.device


