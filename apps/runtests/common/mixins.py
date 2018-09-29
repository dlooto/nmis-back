# coding=utf-8
#
# Created by junn, on 2018/6/13
#

# 测试中使用的基础数据及工具类

import logging

from nmis.projects.consts import PRO_HANDING_TYPE_SELF, PRO_CATE_SOFTWARE
from nmis.projects.models import ProjectPlan, ProjectFlow, ProjectMilestoneState, \
    Milestone, PurchaseContract

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

CONTRACT_DEVICES = [
    {
        "name": "测试系统",
        "producer": "北京仪器",
        "supplier": "聚阳腾达",
        "real_price": 123000,
        "num": 2,
        "real_total_amount": 246000
    },
    {
        "name": "管理系统",
        "producer": "聚阳恒鑫",
        "supplier": "聚阳腾达",
        "real_price": 12000,
        "num": 2,
        "real_total_amount": 24000
    }
]

DEFAULT_MILESTONES = [
    {
        "id": 4001001,
        "title": "需求论证",
        "index": 0
    },
    {
        "id": 4001002,
        "title": "圈定方案",
        "index": 1
    },
    {
        "id": 4001003,
        "title": "采购管理",
        "index": 2
    },
    {
        "id": 4001004,
        "title": "实施验收",
        "index": 3
    },
    {
        "id": 4001005,
        "title": "调研",
        "index": 0,
        "parent_id": 4001002
    },
    {
        "id": 4001006,
        "title": "方案收集",
        "index": 1,
        "parent_id": 4001002
    },
    {
        "id": 4001007,
        "title": "方案论证",
        "index": 2,
        "parent_id": 4001002
    },
    {
        "id": 4001008,
        "title": "确定采购方式",
        "index": 0,
        "parent_id": 4001003
    },
    {
        "id": 4001009,
        "title": "启动采购",
        "index": 1,
        "parent_id": 4001003
    },
    {
        "id": 4001010,
        "title": "合同管理",
        "index": 2,
        "parent_id": 4001003
    },
    {
        "id": 4001011,
        "title": "到货",
        "index": 0,
        "parent_id": 4001004
    },
    {
        "id": 4001012,
        "title": "实施调试",
        "index": 1,
        "parent_id": 4001004
    },
    {
        "id": 4001013,
        "title": "项目验收",
        "index": 2,
        "parent_id": 4001004
    }


]

MILESTONES = [
    {
        "title": "前期准备",
        "index": 1
    },
    {
        "title": "合同签订",
        "index": 2
    },
    {
        "title": "进入实施",
        "index": 3
    },
    {
        "title": "已完成",
        "index": 4
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

    def create_flow(self, organ, milestones=DEFAULT_MILESTONES):
        """

        :param milestones:
        :param flow_data: format like: {"title": "测试流程", "organ": organ}
        :return:
        """
        flow_data = {
            "title": "默认测试流程", "organ": organ, "default_flow": True
        }
        return ProjectFlow.objects.create_flow(milestones, **flow_data)

    def create_default_flow(self, organ, milestones=DEFAULT_MILESTONES):
        flow_data = {
            "title": "项目默认流程", "organ": organ, 'default_flow': True
        }
        return ProjectFlow.objects.create_flow(milestones, **flow_data)

    def get_default_flow(self):
        return ProjectFlow.objects.get_default_flow()

    def init_one_dispatched_project(self, creator, dept, project_cate, title):
        """初始化已分配的项目"""

        project = self.create_project(creator, dept, project_cate, title)

        # 分配项目负责人，同时开启需求论证里程碑
        is_dispatched, msg = project.dispatch(creator)
        return project if is_dispatched else None

    def get_project_milestone_state(self, project, milestone):
        state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        return state if state else None

    def startup_project_milestone_state(self, project, milestone):
        try:
            if isinstance(milestone, str):
                milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone__title=milestone).first()
            if isinstance(milestone, Milestone):
                milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
            milestone_state.status = "DOING"
            milestone_state.save()
            milestone_state.cache()
            return milestone_state
        except Exception as e:
            return None

    def startup_all_project_milestone_state(self, project):
        try:
            milestone_states = ProjectMilestoneState.objects.filter(project=project).all()
            milestone_states.update(status="DOING")
            ProjectMilestoneState.objects.clear_cache(milestone_states)
            return milestone_states
        except Exception as e:
            return []

    def create_purchase_contract(self, project_milestone_state, contract_devices=CONTRACT_DEVICES):

        purchase_contract_data = {
            "contract_no": "BJ20180928",
            "title": "测试合同管理",
            "signed_date": "2018-09-27",
            "seller_contact": "乙方联系人",
            "seller": "乙方单位",
            "seller_tel": "13453453456",
            "buyer_contact": "甲方联系人",
            "total_amount": 1231221,
            "delivery_date": "2018-09-28",
        }
        return PurchaseContract.objects.create_purchase_contract(
            project_milestone_state, contract_devices, **purchase_contract_data)