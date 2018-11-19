# coding=utf-8
#
# Created by junn, on 2018/6/13
#

# 测试中使用的基础数据及工具类

import logging

from nmis.devices.models import MedicalDeviceSix8Cate, AssertDevice, MaintenancePlan, \
    FaultType, RepairOrder, FaultSolution
from nmis.hospitals.models import HospitalAddress
from nmis.projects.consts import PRO_HANDING_TYPE_SELF, PRO_CATE_SOFTWARE
from nmis.projects.models import ProjectPlan, ProjectFlow, ProjectMilestoneState, \
    Milestone, PurchaseContract
from utils import times

logger = logging.getLogger(__name__)


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

MEDICAL_DEVICES_SIX8_CATE = [
    {
        "id": 60030001,
        "code": "6801",
        "title": "基础外科手术器械",
        "level": 1,
        "mgt_cate": 2,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 60030002,
        "code": "6830",
        "title": "医用X射线设备",
        "level": 1,
        "mgt_cate": 3,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 60030003,
        "code": "6801-02",
        "title": "基础外科用刀",
        "level": 2,
        "parent_id": 60030001,
        "example": "手术刀柄和刀片、皮片刀、疣体剥离刀、柳叶刀、铲刀、剃毛刀、皮屑刮刀、挑刀、锋刀、修脚刀、修甲刀、解剖刀",
        "mgt_cate": 1,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 60030004,
        "code": "6801-03",
        "title": "基础外科用剪",
        "level": 2,
        "parent_id": 60030001,
        "example": "普通手术剪、组织剪、综合组织剪、拆线剪、石膏剪、解剖剪、纱布绷带剪、教育用手术剪",
        "mgt_cate": 1,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 60030005,
        "code": "6830-03",
        "title": "X射线手术影像设备",
        "level": 2,
        "parent_id": 60030002,
        "example": "介入治疗X射线机",
        "mgt_cate": 3,
        "created_time": "2018-10-30 15:00"
    }
]

STORAGE_PLACE = [
    {
        "id": 50020001,
        "title": "住院大楼A座",
        "type": "BD",
        "parent_id": None,
        "parent_path": "",
        "level": 1,
        "sort": 1,
        "dept": None,
        "desc": "简介住院大楼A座",
        "disabled": False,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 50020002,
        "title": "综合楼B座",
        "type": "BD",
        "parent_id": None,
        "parent_path": "",
        "level": 1,
        "sort": 2,
        "dept": None,
        "desc": "简介综合楼B座",
        "disabled": False,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 50020003,
        "title": "消毒设备库房001",
        "type": "RM",
        "parent_id": 50020001,
        "parent_path": "50020001",
        "level": 2,
        "sort": 1,
        "desc": "简介消毒设备库房001",
        "disabled": False,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 50020004,
        "title": "消毒设备库房002",
        "type": "RM",
        "parent_id": 50020001,
        "parent_path": "50020001",
        "level": 2,
        "sort": 2,
        "desc": "简介消毒设备库房002",
        "disabled": False,
        "created_time": "2018-10-30 15:00"
    },
    {
        "id": 50020005,
        "title": "手术器械存放室001",
        "type": "RM",
        "parent_id": 50020002,
        "parent_path": "50020002",
        "level": 2,
        "sort": 1,
        "desc": "简介手术器械存放室001",
        "disabled": False,
        "created_time": "2018-10-30 15:00"
    },
]

FAULT_TYPES = [

    {
        "id": 10010001,
        "title": "个人电脑类test",
        "desc": "用于个人电脑类test",
        "parent_id": None,
        "parent_path": "",
        "level": 1,
        "sort": 1,
    },
    {
        "id": 10010002,
        "title": "打印机类test",
        "desc": "用于打印机类test",
        "parent_id": None,
        "parent_path": "",
        "level": 1,
        "sort": 2,
    },
    {
        "id": 10010003,
        "title": "鼠标类test",
        "desc": "用于鼠标类test",
        "parent_id": 10010001,
        "parent_path": "",
        "level": 2,
        "sort": 1,
    },
    {
        "id": 10010004,
        "title": "键盘类test",
        "desc": "用于键盘类test",
        "parent_id": 10010001,
        "parent_path": "",
        "level": 2,
        "sort": 2,
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
            "title": "默认测试流程", "organ": organ, "default_flow": True, "pre_defined": True
        }
        return ProjectFlow.objects.create_flow(milestones, **flow_data)

    def create_default_flow(self, organ, milestones=DEFAULT_MILESTONES):
        flow_data = {
            "title": "项目默认流程", "organ": organ, 'default_flow': True, "pre_defined": True
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


class AssertDevicesMixin(object):

    def create_assert_device(self, title, dept, storage_place, creator, assert_no, bar_code, serial_no):
        """
        创建资产设备
        """
        assert_device_data = {
            "assert_no": assert_no,
            "title": title,
            "serial_no": serial_no,
            "type_spec": "BN3004",
            "service_life": 3,
            "responsible_dept_id": dept.id,
            "production_date": "2018-09-12",
            "bar_code": bar_code,
            "status": "US",
            "storage_place_id": storage_place.id,
            "purchase_date": "2018-10-09",
            "cate": "IN",
            "creator_id": creator.id
        }
        try:
            return AssertDevice.objects.create(**assert_device_data)
        except Exception as e:
            logger.exception(e)
            return None

    def create_medical_device_cate(self, creator):
        """
        创建资产设备医疗器械分类数据
        :return:
        """
        medical_cate_data = {
            "code": "6801-02",
            "title": "基础外科用刀",
            "level": 2,
            "example": "手术刀柄和刀片、皮片刀、疣体剥离刀、柳叶刀、铲刀、剃毛刀、皮屑刮刀、挑刀、锋刀、修脚刀、修甲刀、解剖刀",
            "mgt_cate": 1,
            "created_time": "2018-10-30 15:00"
        }
        medical_cate_parent_data = {
            "code": "6801",
            "title": "基础外科手术器械",
            "level": 2,
            "example": "",
            "created_time": "2018-10-30 15:00"
        }
        medical_device_cate = MedicalDeviceSix8Cate.objects.create(
            creator=creator, **medical_cate_parent_data)
        logger.info(medical_device_cate)
        return MedicalDeviceSix8Cate.objects.create(
            parent=medical_device_cate, creator=creator, **medical_cate_data)

    def get_assert_device(self, assert_device_id):

        return AssertDevice.objects.filter(id=assert_device_id).first()

    def create_maintenance_plan(self, title, storage_places, executor, creator, assert_devices, type="PL"):
        """
        创建资产设备维护计划
        """
        start_date = times.now().strftime('%Y-%m-%d')
        expired_date = times.after_days(20).strftime('%Y-%m-%d')
        m_plan_data = {
            "plan_no": "",
            "title": title,
            "type": type,
            "start_date": start_date,
            "expired_date": expired_date,
            "executor_id": executor.id,
            "creator_id": creator.id
        }
        try:
            return MaintenancePlan.objects.create_maintenance_plan(storage_places, assert_devices, **m_plan_data)
        except Exception as e:
            logger.exception(e)
            return None

    def init_fault_types(self, creator, fault_type_jsons=FAULT_TYPES):

        fault_types = list()
        for item in fault_type_jsons:
            ft = FaultType.objects.model(
                id=item.get('id'),
                title=item.get('title'),
                desc=item.get('desc'),
                sort=item.get('sort'),
                parent_id=item.get('parent_id'),
                parent_path=item.get('parent_path'),
                level=item.get('level'),
                creator=creator,

            )
            fault_types.append(ft)
        return FaultType.objects.bulk_create(fault_types)

    def init_repair_orders(self, creator, applicant, fault_types=None):
        if not fault_types:
            fault_types = self.init_fault_types(creator)
        order_one = RepairOrder.objects.create_order(applicant, fault_types[0], 'office无法使用', creator)
        order_two = RepairOrder.objects.create_order(applicant, fault_types[1], '呼吸机无法使用', creator)
        return [order_one, order_two]

    def create_repair_order(self, applicant, fault_type, desc, creator, order_no):
        data = {
            'applicant': applicant, 'fault_type': fault_type,
            'order_no': order_no,  'desc': desc, 'creator': creator
        }
        RepairOrder.objects.create(**data)

    def create_fault_solution(self, title, fault_type, desc, solution, creator):
        data = {
            'title': title,
            'fault_type': fault_type,
            'desc': desc,
            'solution': solution,
            'creator': creator,
        }
        return FaultSolution.objects.create(**data)


class HospitalMixin(object):

    def create_storage_places(self, dept, storage_places=STORAGE_PLACE):
        """
        创建资产设备存储地点集
        :param dept:
        :param storage_places:
        :return:
        """
        for sp in storage_places:
            sp['dept'] = sp.get('dept', dept)
        return HospitalAddress.objects.create_storage_place(storage_places)

    def create_storage_place(self, dept, parent, title):
        """
        创建大楼中的存储地点
        :param dept: 存储地点所属科室
        :param parent: 存储地点所属大楼
        :param title: 存储地点名称
        """

        try:
            return HospitalAddress.objects.create(
                dept=dept, parent=parent, title=title, type="RM", level=2, sort=1, disabled=False, created_time=times.now())
        except Exception as e:
            logger.exception(e)
            return None

    def create_hospital_address(self, title):
        """
        创建机构中某个大楼信息
        :param title: 大楼名称
        """
        from nmis.hospitals.models import HospitalAddress
        return HospitalAddress.objects.create(
            title=title, type="RM", level=2, sort=1,  disabled=False, created_time=times.now())
