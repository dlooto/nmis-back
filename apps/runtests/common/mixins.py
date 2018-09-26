# coding=utf-8
#
# Created by junn, on 2018/6/13
#

# 测试中使用的基础数据及工具类

import logging

from nmis.projects.consts import PRO_HANDING_TYPE_SELF, PRO_CATE_SOFTWARE
from nmis.projects.models import ProjectPlan, ProjectFlow

logs = logging.getLogger(__name__)


ORDERED_DEVICES = [
    {
        "name": "胎心仪",
        "type_spec": "PE29-1389",
        "num": 2,
        "measure": "台",
        "purpose": "用来测胎儿心电",
        "planned_price": 15000.0
    },
    {
        "name": "理疗仪",
        "type_spec": "ST19-1399",
        "num": 4,
        "measure": "台",
        "purpose": "心理科室需要",
        "planned_price": 25000.0
    }
]

SOFTWARE_DEVICES = [
    {
        "name": "易冉单点登录",
        "purpose": "统一登录，统一管理",
        "planned_price": 100000.0
    },
    {
        "name": "易冉运维信息服务系统",
        "purpose": "解决医院设备管理",
        "planned_price": 200000.0
    }
]

MILESTONES = [
    {
        "id": 3001001,
        "title": "需求论证",
        "index": 0
    },
    {
        "id": 3001002,
        "title": "圈定方案",
        "index": 1
    },
    {
        "id": 3001003,
        "title": "采购管理",
        "index": 2
    },
    {
        "id": 3001004,
        "title": "实施验收",
        "index": 3
    },
    {
        "id": 3001005,
        "title": "调研",
        "index": 0,
        "parent_id": 3001002
    },
    {
        "id": 3001006,
        "title": "方案收集",
        "index": 1,
        "parent_id": 3001002
    },
    {
        "id": 3001007,
        "title": "方案论证",
        "index": 2,
        "parent_id": 3001002
    },
    {
        "id": 3001008,
        "title": "确定采购方式",
        "index": 0,
        "parent_id": 3001003
    },
    {
        "id": 3001009,
        "title": "启动采购",
        "index": 1,
        "parent_id": 3001003
    },
    {
        "id": 3001010,
        "title": "合同管理",
        "index": 2,
        "parent_id": 3001003
    },
    {
        "id": 3001011,
        "title": "到货",
        "index": 0,
        "parent_id": 3001004
    },
    {
        "id": 3001012,
        "title": "实施调试",
        "index": 1,
        "parent_id": 3001004
    },
    {
        "id": 3001013,
        "title": "项目验收(完结点)",
        "index": 2,
        "parent_id": 3001004
    }


]


class ProjectPlanMixin(object):
    """
    项目管理基础工具类
    """

    def create_project(self, creator, dept, project_cate="HW", title="设备采购",
                       handing_type='AG', ordered_devices=ORDERED_DEVICES,
                       software_devices=SOFTWARE_DEVICES):
        """

        :param creator: 项目创建者
        :param dept: 项目归属科室
        :param project_cate: 项目类型（HW：医疗器械项目，SW：信息化项目，默认为医疗器械项目）
        :param title: 项目名称
        :param handing_type: 项目办理类型(AG: 转交办理，SE: 自主办理)
        :param ordered_devices: 硬件设备
        :param software_devices: 软件设备
        :return:
        """
        project_data = {
            'title': title,
            'handing_type': handing_type,
            'project_cate': project_cate,
            'purpose': "设备老旧换新",
            'project_introduce': '项目介绍',
            'creator': creator,
            'related_dept': dept,
            'pre_amount': 430000.0
        }

        if handing_type == PRO_HANDING_TYPE_SELF:
            project_data['performer'] = creator

        if project_cate == PRO_CATE_SOFTWARE:
            return ProjectPlan.objects.create_project(
                hardware_devices=ordered_devices, software_devices=software_devices, **project_data
            )
        return ProjectPlan.objects.create_project(hardware_devices=ordered_devices, **project_data)

    def create_flow(self, organ, milestones=MILESTONES):
        """

        :param milestones:
        :param flow_data: format like: {"title": "测试流程", "organ": organ}
        :return:
        """
        flow_data = {
            "title": "默认测试流程", "organ": organ, "default_flow": True
        }
        return ProjectFlow.objects.create_flow(milestones, **flow_data)