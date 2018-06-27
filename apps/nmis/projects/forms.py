# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging
from itertools import chain
from base.forms import BaseForm
from nmis.projects.models import ProjectPlan, ProjectFlow
from nmis.projects.consts import PROJECT_STATUS_CHOICES
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

    def check_devices(self):
        return True

    def save(self):
        data = {
            'title': self.data.get('project_title', '').strip(),
            'purpose': self.data.get('purpose', '').strip(),
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
            'flow_is_used':    '流程已经在使用在，不能修改',
            "err_flow_title": "流程标题错误",
        })

    def is_valid(self):
        if self.check_flow_used():
            return
        return self.check_flow_title()

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
        return self.old_flow.update(data)


class ProjectPlanListForm(BaseForm):
    def __init__(self, req, hospital, *args, **kwargs):
        BaseForm.__init__(self, req, hospital, *args, **kwargs)

        self.req = req
        self.hospital = hospital

        self.ERR_CODES.update({
            "err_expired_date": "截止时间必须为一个时间段",
            "err_status": "项目状态错误"
        })

    def is_valid(self):
        return self.check_expired_date() and self.check_status()

    def check_expired_date(self):

        # 如果时间段不存在，直接返回true
        if not self.req.GET.get('upper_expired_date') and \
                not self.req.GET.get('lower_expired_date'):
            return True

        # 时间段中只存在一个时间，直接返回false
        if not self.req.GET.get('upper_expired_date') or \
                not self.req.GET.get('lower_expired_date'):
            self.update_errors('expired_date', 'err_expired_date')
            return False
        return True

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
        else:
            data['status__in'] = dict(PROJECT_STATUS_CHOICES).keys()

        if self.req.GET.get('creator_id', ''):
            data['creator_id'] = self.req.GET.get('creator_id', '').strip()

        if self.req.GET.get('performer_id', ''):
            data['performer_id'] = self.req.GET.get('performer_id', '').strip()

        if self.req.GET.get('current_stone_id', ''):
            data['current_stone_id'] = self.req.GET.get('current_stone_id').strip()

        if self.req.GET.get('upper_expired_date', '').strip() and \
                self.req.GET.get('lower_expired_date', '').strip():
            data['created_time__lte'] = self.req.GET.get('upper_expired_date', '').strip()
            data['created_time__gte'] = self.req.GET.get('lower_expired_date', '').strip()

        # 判断是否存在项目名和项目负责人关键字
        if self.req.GET.get('pro_title_leader', '').strip():

            staffs = Staff.objects.get_staffs_by_name(
                self.hospital, self.req.GET.get('pro_title_leader', '').strip()
            )

            return ProjectPlan.objects.get_projects_vague(
                self.hospital,
                self.req.GET.get('pro_title_leader', '').strip(),
                staffs, **data)

        return ProjectPlan.objects.get_projects(self.hospital, **data)
