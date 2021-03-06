# coding=utf-8
#
# Created by junn, on 2018/6/11
#

# 

import logging

from django.core.files.uploadedfile import UploadedFile

import settings
from nmis.projects.consts import (PRO_HANDING_TYPE_AGENT, PRO_STATUS_STARTED,
                                  PRO_CATE_SOFTWARE, PRO_CATE_HARDWARE,
                                  PRO_STATUS_OVERRULE, PRO_OPERATION_OVERRULE,
                                  PRO_OPERATION_PAUSE, PRO_STATUS_PAUSE,
                                  PRO_MILESTONE_DOING)
from nmis.projects.models import ProjectDocument, ProjectPlan, ProjectMilestoneState, \
    ProjectFlow, Milestone
from runtests import BaseTestCase
from runtests.common.mixins import ProjectPlanMixin
from utils.files import upload_file, remove

logger = logging.getLogger(__name__)


class ProjectApiTestCase(BaseTestCase, ProjectPlanMixin):
    """
    项目管理相关APi测试
    """

    project_create_api = '/api/v1/projects/create'  # 项目创建
    single_project_api = '/api/v1/projects/{}'      # 单个项目操作API接口
    project_milestone_change_api = '/api/v1/projects/{}/change-milestone'

    def test_project_detail(self):
        """
        项目详情
        """
        self.login_with_username(self.user)

        # 医院员工都可查看项目详情
        data = {
            "organ_id": self.organ.id,
        }
        project = self.create_project(self.admin_staff, self.dept, title="新项目")
        response = self.get(self.single_project_api.format(project.id), data=data)
        self.assert_response_success(response)
        self.assertIsNotNone(response.get("project"))
        self.assertEqual(response.get("project").get('title'), project.title)

    def test_project_update(self):
        """
        修改项目
        """

        self.login_with_username(self.user)
        # 创建医疗器械项目和信息化项目
        hardware_project = self.create_project(self.admin_staff, self.dept, project_cate='HW', title="医疗器械项目", handing_type='SE')
        software_project = self.create_project(self.admin_staff, self.dept, project_cate="SW", title="信息化项目", handing_type='SE')
        hardware_old_devices = hardware_project.get_hardware_devices()

        hardware_added_devices = [
            {
                "name": "胎心仪Csnew",
                "type_spec": "CS29-1001",
                "num": 12,
                "measure": "架",
                "purpose": "用来测胎儿心电cs",
                "planned_price": 15001.0
            },
            {
                "name": "理疗仪Csnew",
                "type_spec": "CS19-1002",
                "num": 11,
                "measure": "个",
                "purpose": "心理科室需要cs",
                "planned_price": 25002.0
            },
        ]
        hardware_updated_devices = [
            {
                "id": hardware_old_devices[0].id,
                "name": "胎心仪CsUP",
                "type_spec": "CS29-1003",
                "num": 20,
                "measure": "架",
                "purpose": "用来测胎儿心电cs",
                "planned_price": 2002.0
            },
            {
                "id": hardware_old_devices[1].id,
                "name": "理疗仪CsUP",
                "type_spec": "CS19-1004",
                "num": 21,
                "measure": "个",
                "purpose": "心理科室需要cs",
                "planned_price": 2001.0
            },
        ]
        software_added_devices = [
            {
                "name": "说好的系统呢",
                "purpose": "有卵用",
                'planned_price': 234
            },
            {
                "name": "牛逼的系统",
                "purpose": "有卵用",
                'planned_price': 234
            }
        ]
        software_updated_devices = [
            {
                "id": software_project.get_software_devices()[0].id,
                "name": "修改系统名",
                "purpose": "修改系统用途",
                'planned_price': 123
            },
            {
                "id": software_project.get_software_devices()[1].id,
                "name": "修改的系统名",
                "purpose": "修改的系统用途",
                'planned_price': 123
            }
        ]

        project_base_data = {
            "organ_id": self.organ.id,
            "project_title": "新的项目名称",
            "purpose": "修改后的用途说明",
            'handing_type': 'SE',
            'hardware_added_devices': hardware_added_devices,
            'hardware_updated_devices': hardware_updated_devices,
        }
        # 测试修改医疗器械项目申请
        response = self.put(self.single_project_api.format(hardware_project.id), data=project_base_data)
        self.assert_response_success(response)
        new_project = response.get('project')
        self.assertIsNotNone(new_project)
        self.assertEqual(new_project.get('title'), project_base_data['project_title'])
        self.assertEqual(new_project.get('handing_type'), project_base_data['handing_type'])
        devices = new_project.get('hardware_devices')
        self.assertIsNotNone(devices)
        for item in devices:
            for im in hardware_updated_devices:
                if item['id'] == im['id']:
                    self.assertEqual(item['name'], im['name'])
                    self.assertEqual(item['type_spec'], im['type_spec'])
                    self.assertEqual(item['num'], im['num'])

                elif item['name'] == im['name']:
                    self.assertEqual(item['measure'], im['measure'])
                    self.assertEqual(item['purpose'], im['purpose'])
                    self.assertEqual(item['planned_price'], im['planned_price'])

        # 测试修改信息化项目
        software_project_data = {
            "organ_id": self.organ.id,
            "project_title": "信息化项目",
            "purpose": "修改后的用途说明",
            'handing_type': 'SE',
            'hardware_added_devices': hardware_added_devices,
            'hardware_updated_devices': hardware_updated_devices,
            'software_added_devices': software_added_devices,
            'software_updated_devices': software_updated_devices

        }
        resp = self.put(self.single_project_api.format(software_project.id), data=software_project_data)
        self.assert_response_success(resp)
        project = resp.get('project')
        hardware_devices = project.get('hardware_devices')
        software_devices = project.get('software_devices')
        self.assertIsNotNone(hardware_devices)
        self.assertIsNotNone(software_devices)
        self.assertEqual(len(hardware_devices), 4)
        self.assertEqual(len(software_devices), 4)

        for i in range(len(software_added_devices)):
            self.assert_object_in_results(software_added_devices[i], software_devices)

        for i in range(len(software_updated_devices)):
            self.assert_object_in_results(software_updated_devices[i], software_devices)

        for i in range(len(hardware_added_devices)):
            self.assert_object_in_results(hardware_added_devices[i], hardware_devices)

    def test_project_del(self):
        """
        删除项目API接口测试(已分配的项目不能被删除)
        """
        self.login_with_username(self.user)
        # 创建项目
        organ_id = {
            "organ_id": self.organ.id
        }
        project = self.create_project(self.admin_staff, self.dept, title="测试项目")

        response = self.delete(
            self.single_project_api.format(project.id)
        )

        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)

        # 测试项目被使用，不能删除
        new_project = self.create_project(self.admin_staff, self.dept, title='新的测试项目')
        new_project.performer = self.admin_staff
        new_project.save()

        response2 = self.delete(
            self.single_project_api.format(new_project.id)
        )

        self.assert_response_failure(response2)
        self.assertEqual(response2.get('code'), 0)
        self.assertEqual(response2.get('msg'), '项目已被分配，无法删除')

    def test_project_create(self):
        """
        api测试: 创建项目申请
        """

        self.login_with_username(self.user)

        # 测试自行办理、信息化项目申请
        project_data = {
            "organ_id": self.organ.id,
            "project_title": "牛逼项目1",
            "handing_type": "SE",
            "pro_type": PRO_CATE_SOFTWARE,
            "purpose": "牛逼的不能为外人说道的目标",
            "creator_id": self.admin_staff.id,
            "related_dept_id": self.admin_staff.dept.id,
            'pre_amount': 1212312,
            "hardware_devices": [
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
                    "num": 5,
                    "measure": "台",
                    "purpose": "心理科室需要",
                    "planned_price": 25000.0
                }
            ],
            "software_devices": [
                {
                    "name": "易冉单点登录",
                    "purpose": "单点登录",
                    'planned_price': 1231231
                }
            ]
        }

        response = self.post(self.project_create_api, data=project_data)
        self.assert_response_success(response)

        result_project = response.get('project')
        self.assertIsNotNone(result_project)
        self.assertEqual(project_data['project_title'], result_project.get('title'))
        self.assertEqual(project_data['handing_type'], result_project.get('handing_type'))

        self.assertEqual(
            len(result_project.get('hardware_devices')), len(project_data.get('hardware_devices'))
        )
        self.assertEqual(
            len(result_project.get('software_devices')), len(project_data.get('software_devices'))
        )
        self.assert_object_in_results(project_data.get('hardware_devices')[0],
                                      result_project.get('hardware_devices'))
        self.assertEqual(project_data.get('pro_type'), result_project.get('project_cate'))

        # 测试转交办理、医疗器械设备项目申请
        pro2_data = project_data
        pro2_data['handing_type'] = PRO_HANDING_TYPE_AGENT
        pro2_data['pro_type'] = PRO_CATE_HARDWARE

        resp2 = self.post(self.project_create_api, data=pro2_data)
        self.assert_response_success(resp2)
        pro2 = resp2.get('project')
        self.assertIsNotNone(pro2)
        self.assertEqual(pro2_data['handing_type'], pro2.get('handing_type'))
        self.assertIsNone(pro2.get('performer_id'))
        self.assertEqual(pro2_data.get('pro_type'), pro2.get('project_cate'))
        self.assertEqual(len(pro2_data.get('hardware_devices')), len(pro2.get('hardware_devices')))
        self.assertEqual(len(pro2.get('software_devices')), 0)

    def test_my_project_list(self):
        """
        api测试：项目总览列表
        """
        api = "/api/v1/projects/"

        self.login_with_username(self.user)
        for index in range(0, 5):
            self.create_project(
                self.admin_staff, self.dept, title='测试项目_{}'.format(self.get_random_suffix())
            )

        project_data = {
            'pro_status': 'PE',
            'search_key': '测试',
            'page': 1,
            'size': 4
        }

        response = self.get(api, data=project_data)

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('projects'))
        self.assertEqual(len(response.get('projects')), 4)
        self.assert_object_in_results(
            {'creator_id': self.admin_staff.id}, response.get('projects')
        )

    def test_undispatched_project_list(self):
        """
        api测试：待分配项目api接口测试
        """
        api = "/api/v1/projects/undispatched"

        self.login_with_username(self.user)
        # 创建一个待分配项目
        project1 = self.create_project(self.admin_staff, self.dept, title='我是待分配项目1')
        project2 = self.create_project(self.admin_staff, self.dept, title='我是待分配项目2')

        response = self.get(api)

        self.assert_response_success(response)
        results = response.get('projects')
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2)
        self.assert_object_in_results({'title': project1.title}, results)

    def test_performed_list(self):
        """
        API测试: 测试我负责的项目申请列表
        """
        api = '/api/v1/projects/performed'

        self.login_with_username(self.user)
        # 创建项目列表
        projects = []
        for index in range(0, 5):
            project = self.create_project(self.admin_staff, self.dept, project_cate='SW',
                                          title='测试项目{}'.format(self.get_random_suffix()))
            projects.append(project)
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        # 分配项目负责人
        for i in range(len(projects)):
            projects[i].dispatch(self.admin_staff)
        data = {
            'search_key': '项目',
            'pro_status': 'SD'
        }

        response = self.get(api, data=data)
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('projects'))
        self.assertEqual(len(response.get('projects')), 5)
        self.assert_object_in_results({'performer_name': self.admin_staff.name}, response.get('projects'))

    def test_applied_projects(self):
        """
        API测试: 测试我申请的项目列表
        """
        api = '/api/v1/projects/applied'

        self.login_with_username(self.user)
        projects = []
        for i in range(0, 5):
            project = self.create_project(
                self.admin_staff, self.dept, project_cate='SW', title='测试项目{}'.format(self.get_random_suffix())
            )
            projects.append(project)
        data = {
            'pro_status': 'PE',
            'search_key': '项目'
        }

        response = self.get(api, data=data)

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('projects'))
        self.assertEqual(len(response.get('projects')), 5)
        self.assert_object_in_results(
            {'creator_name': self.admin_staff.name}, response.get('projects')
        )

    def test_project_redispatch(self):
        """
        API测试：重新分配项目给负责人接口测试(只需分配项目负责人，不改变里程碑状态， 只改变项目负责人信息)
        """
        api = '/api/v1/projects/{}/redispatch'
        self.login_with_username(self.user)
        # 创建项目
        project_plan = self.create_project(self.admin_staff, self.dept, title='待分配项目')
        default_flow = self.create_default_flow(self.organ)


        # 分配项目
        success = project_plan.dispatch(self.admin_staff)
        self.assertTrue(success)
        self.assertIsNotNone(project_plan.performer)
        self.assertEqual(self.admin_staff.id, project_plan.performer.id)

        # 重新分配项目
        # 初始化staff相应数据
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        staff = self.create_completed_staff(self.organ, self.dept, name='负责人', **staff_data)

        data = {
            'performer_id': staff.id,
        }
        response = self.put(api.format(project_plan.id), data=data)

        self.assert_response_success(response)
        project = response.get('project')
        self.assertIsNotNone(project.get('performer_id'))
        self.assertEqual(staff.id, project.get('performer_id'))

    def test_project_dispatch(self):
        """
        API测试：分配项目负责人（分配默认流程，改变项目状态，项目直接进入默认流程的需求论证里程碑）
        """
        api = '/api/v1/projects/{}/dispatch'

        self.login_with_username(self.user)

        # 创建项目
        project_plan = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='新建项目申请')
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        # 只分配项目负责人
        data = {
            'performer_id': self.admin_staff.id,
        }
        response = self.put(api.format(project_plan.id), data=data)
        self.assert_response_success(response)
        project = response.get('project')
        self.assertIsNotNone(project.get('performer_id'))
        self.assertEqual(project_plan.id, project.get('id'))
        self.assertEqual(self.admin_staff.id, project.get('performer_id'))
        # 同时分配项目负责人和项目协助办理人
        project_plan2 = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='新建项目申请2')
        # 创建项目协助人
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        assistant = self.create_completed_staff(self.organ, self.dept, name='项目协助办理人', **staff_data)

        data = {
            'performer_id': self.admin_staff.id,
            'assistant_id': assistant.id
        }
        response2 = self.put(api.format(project_plan2.id), data=data)
        self.assert_response_success(response2)
        project2 = response2.get('project')
        self.assertIsNotNone(project2.get('performer_id'))
        self.assertEqual(project_plan2.id, project2.get('id'))
        self.assertEqual(self.admin_staff.id, project2.get('performer_id'))
        self.assertIsNotNone(project2.get('assistant_id'))
        self.assertEqual(assistant.id, project2.get('assistant_id'))

    def test_project_startup(self):
        """
        API测试：启动项目接口测试(可选择协助执行人，选择项目截止时间，项目启动后状态变更为已启动)
        """
        api = '/api/v1/projects/{}/startup'

        self.login_with_username(self.user)
        # 启动有协助办理人项目测试
        project1 = self.create_project(self.admin_staff, self.dept, title='待启动项目T1',
                                       handing_type='SE')
        # 启动无协助办理人项目 测试
        project2 = self.create_project(self.admin_staff, self.dept, title='待启动项目T2',
                                       handing_type='SE')
        flow = self.create_flow(self.organ)
        data1 = {
            'expired_time': '2018-12-01 00:00:00',
            'flow_id': flow.id,
            'assistant_id': self.admin_staff.id,
        }
        data2 = {
            'expired_time': '2018-12-01 00:00:00',
            'flow_id': flow.id,
        }
        reps1 = self.put(api.format(project1.id), data=data1)
        reps2 = self.put(api.format(project2.id), data=data2)

        self.assert_response_success(reps1)
        pro1 = reps1.get('project')
        self.assertIsNotNone(pro1)
        self.assertEqual(pro1.get('status'), PRO_STATUS_STARTED)
        self.assertEqual(pro1.get('assistant_id'), self.admin_staff.id)
        self.assertIsNotNone(pro1.get('startup_time'))
        self.assertEqual(pro1.get('expired_time'), data1.get('expired_time'))

        self.assert_response_success(reps2)
        pro2 = reps2.get('project')
        self.assertIsNotNone(pro2)
        self.assertEqual(pro2.get('status'), PRO_STATUS_STARTED)
        self.assertIsNone(pro2.get('assistant_id'))
        self.assertIsNotNone(pro2.get('startup_time'))
        self.assertEqual(pro2.get('expired_time'), data1.get('expired_time'))

    def test_projects_applied(self):
        """
        API测试：我申请的项目列表接口测试
        """
        api = '/api/v1/projects/'
        self.login_with_username(self.user)
        # 创建项目
        for index in range(0, 3):
            self.create_project(
                self.admin_staff, self.dept,
                title='我是申请的项目_{}'.format(self.get_random_suffix()))

        data = {
            'organ_id': self.organ.id,
            'type': 'apply'
        }

        response = self.get(api, data=data)
        self.assert_response_success(response)
        projects = response.get('projects')
        self.assertIsNotNone(projects)
        self.assertEqual(len(projects), 3)
        self.assert_object_in_results({'creator_id': self.admin_staff.id}, projects)

    def test_projects_my_performer(self):
        """
        API测试：我负责的项目列表接口测试
        """
        api = '/api/v1/projects/'
        self.login_with_username(self.user)

        # 创建项目
        for index in range(0, 3):
            project = self.create_project(
                self.admin_staff, self.dept, title='我负责的项目_{}'.format(self.get_random_suffix())
            )
            project.performer = self.admin_staff
            project.save()

        data = {
            'organ_id': self.organ.id,
            'pro_status': 'PE',
            'search_key': '项目',
            'type': 'my_performer'
        }
        response = self.get(api, data=data)

        self.assert_response_success(response)
        projects = response.get('projects')
        self.assertIsNotNone(projects)
        self.assertEqual(len(projects), 3)

    def test_projects_overrule(self):
        """
        API测试: 项目负责人驳回项目申请
        """
        api = '/api/v1/projects/{}/overrule'
        self.login_with_username(self.user)
        # 创建项目
        project = self.create_project(self.admin_staff, self.dept, project_cate="SW", title="测试被驳回项目")
        data = {
            'project': project.id,
            'reason': '预算太高',
            'operation': PRO_OPERATION_OVERRULE
        }
        response = self.put(api.format(project.id), data=data)

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project'))
        self.assertEqual(response.get('project').get('status'), PRO_STATUS_OVERRULE)

    def test_dispatched_project_list(self):
        """
        API测试: 获取已分配项目列表
        """
        api = '/api/v1/projects/dispatched'

        self.login(self.user)
        projects = []
        # 创建项目
        for index in range(0, 5):
            project = self.create_project(
                self.admin_staff, self.dept, title='测试项目_{}'.format(self.get_random_suffix())
            )
            projects.append(project)
        # 创建默认流程
        defalut_flow = self.create_flow(self.organ)

        project_data = {
            'page': 1,
            'size': 4
        }

        # 分配项目
        for index in range(len(projects)):
            projects[index].dispatch(self.admin_staff)

        response = self.get(api, data=project_data)

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('projects'))
        self.assertEqual(len(response.get('projects')), 4)

    def test_pause_project(self):
        """
        API测试:测试项目负责人挂起项目
        """
        api = '/api/v1/projects/{}/pause'

        self.login_with_username(self.user)

        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试挂起项目')
        default_flow = self.create_default_flow(self.organ)
        # 分配项目负责人
        project.dispatch(self.admin_staff)

        data = {
            'project': project.id,
            'reason': '由于供应商原因导致项目被挂起',
            'operation': PRO_OPERATION_PAUSE
        }

        response = self.put(api.format(project.id), data=data)

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project'))
        self.assertEqual(response.get('project').get('status'), PRO_STATUS_PAUSE)

    def test_cancel_pause_project(self):
        """
        API测试:测试项目负责人取消项目挂起
        """
        api = '/api/v1/projects/{}/cancel-pause'

        self.login_with_username(self.user)
        # 创建测试项目
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        # 创建测试项目默认流程
        default_flow = self.create_flow(self.organ)
        # 分配项目
        self.assertTrue(project.dispatch(self.admin_staff))

        response = self.put(api.format(project.id))

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project'))
        self.assertEqual(response.get('project').get('status'), PRO_STATUS_STARTED)

    def test_dispatched_assistant(self):
        """
        API测试: 测试负责人分配项目的协助办理人
        """
        api = '/api/v1/projects/{}/dispatch-assistant'

        self.login_with_username(self.user)

        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='分配项目协助办理人')

        # 创建项目协助人
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        staff = self.create_completed_staff(self.organ, self.dept, name='负责人', **staff_data)

        default_flow = self.create_flow(self.organ)
        # 分配项目负责人
        self.assertTrue(project.dispatch(self.admin_staff))
        data = {
            'assistant_id': staff.id
        }
        response = self.put(api.format(project.id), data=data)

        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)

    def test_assisted_projects(self):
        """
        API测试: 测试获取我协助的项目列表
        """
        api = "/api/v1/projects/assisted"

        self.login_with_username(self.user)

        # 创建项目
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        # 创建默认流程
        defalut_flow = self.create_flow(self.organ)
        # 创建项目负责人
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        performer_staff = self.create_completed_staff(self.organ, self.dept, name="协助人",
                                                      **staff_data)
        # 分配项目负责人
        self.assertTrue(project.dispatch(performer_staff))

        # 分配项目协助人
        self.assertTrue(project.dispatched_assistant(self.admin_staff))

        response = self.get(api)
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('projects'))
        self.assertEqual(response.get('projects')[0].get('assistant_id'), self.admin_staff.id)

    # def test_single_upload_file(self):
    #     """
    #     API测试：测试单个文件上传接口
    #     """
    #     api = "/api/v1/projects/{}/single-upload-file"
    #     import os
    #     self.login_with_username(self.user)
    #     # 返回当前脚本路径
    #     curr_path = os.path.dirname(__file__)
    #
    #     # 创建项目
    #     project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
    #
    #     with open(curr_path + '/data/upload_file_test.xlsx', 'wb+') as file_obj:
    #
    #       response = self.raw_post(api.format(project.id), {'file_key': file_obj})
    #
    #     self.assert_response_success(response)
    #     self.assertIsNotNone(response.get('file_url'))
    #
    #     upload_path = '%s%s' % (self.DOC_TEST_DIR, 'upload_file_test.xlsx')
    #     self.assertEqual(upload_path, response.get('file_url'))
    #     file_obj.close()

    def test_deleted_single_file(self):
        """
        API测试：测试上传/删除单个文件接口
        """
        import os
        upload_file_api = "/api/v1/projects/{}/single-upload-file"  # 上传文件API接口

        delete_file_api = '/api/v1/projects/single-del-file/{}'  # 删除文件API接口

        self.login_with_username(self.user)
        # 创建项目申请
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')

        # 判断是否存在默认流程
        default_flow = ProjectFlow.objects.get_default_flow()
        if not default_flow:
            default_flow = self.create_flow(self.organ)
        # 分配流程
        self.assertTrue(project.dispatch(self.admin_staff))

        new_project = ProjectPlan.objects.filter(id=project.id).first()
        self.assertEqual(new_project.attached_flow, default_flow)
        # 获取第一个主里程碑
        first_main_milestone = default_flow.get_first_main_milestone()

        # 获取第一个project_milestone_state
        first_pro_mil_state = ProjectMilestoneState.objects.get_pro_milestone_state_by_project_milestone(
            project=project, milestone=first_main_milestone)

        # 上传文件
        curr_path = os.path.dirname(__file__)

        with open(curr_path + '/data/upload_file_test.xlsx', 'wb+') as file_obj:

            upload_response = self.raw_post(upload_file_api.format(project.id), {'file_key': file_obj})

        self.assert_response_success(upload_response)
        self.assertIsNotNone(upload_response.get('file_url'))

        upload_path = '{}{}'.format(self.DOC_TEST_DIR, 'upload_file_test.xlsx')
        success_upload_file_path = upload_response.get('file_url')  # 获取上传成功后的路径

        # self.assertEqual(upload_path, success_upload_file_path)
        project_document_data = {
            'name': 'upload_file_test.xlsx',
            'category': 'others',
            'path': success_upload_file_path,
        }
        project_documents = [project_document_data]
        doc_list = ProjectDocument.objects.bulk_save_or_update_project_doc(project_documents)
        self.assertIsNotNone(doc_list)
        doc_id_str = ','.join('%s' % doc.id for doc in doc_list)

        # 保存doc到ProjectMilestoneState
        self.assertTrue(first_pro_mil_state.save_doc_list(doc_id_str))
        # 断言当前ProjectDocument是否在ProjectMilestoneState中
        self.assertTrue(str(doc_list[0].id) in first_pro_mil_state.doc_list)

        # 删除附件
        doc_id = doc_list[0].id

        delete_file_response = self.post(
            delete_file_api.format(doc_id), data={'project_milestone_state_id': first_pro_mil_state.id})
        self.assert_response_success(delete_file_response)
        self.assertEqual(10000, delete_file_response.get('code'))
        pro_mil_state = ProjectMilestoneState.objects.get_pro_milestone_state_by_project_milestone(
            project=project, milestone=first_main_milestone)
        # 断言删除附件后，当前ProjectDocument是否在ProjectMilestoneState中
        self.assertTrue(str(doc_list[0].id) not in pro_mil_state.doc_list)


class ProjectMilestoneStateTest(BaseTestCase, ProjectPlanMixin):

    def test_get_common_project_milestone_state_info(self):
        """
        测试获取通用的项目里程碑下的信息：调研、实时调试、项目验收
        :return:
        """
        api = '/api/v1/projects/{0}/project_milestone_states/{1}/get-research-info'

        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目x001')
        if not self.get_default_flow():
            self.create_default_flow(self.organ)
        is_dispatched, msg = project.dispatch(self.admin_staff)

        self.assertTrue(is_dispatched, msg)
        self.assertEqual(project.status, "SD")

        main_milestone1 = project.attached_flow.get_first_main_milestone()
        main_milestone_state1 = self.get_project_milestone_state(project=project, milestone=main_milestone1)
        self.assertTrue(main_milestone_state1.is_in_process())

        main_milestone2 = main_milestone1.next()

        main_milestone_state2 = self.get_project_milestone_state(project=project, milestone=main_milestone2)

        self.assertTrue(main_milestone_state2.is_unstarted())

        main_milestone2_child1 = main_milestone2.next()

        main_milestone_state2_child1 = self.get_project_milestone_state(project=project, milestone=main_milestone2_child1)

        # 变更需求论证里程碑，开启圈定方案-调研里程碑
        changed, msg = project.change_project_milestone_state(main_milestone_state1)
        self.assertTrue(changed, msg)
        # self.assertEqual(main_milestone_state2_child1.milestone.title, '')
        self.assertTrue(project.status == "SD")

        # 项目里程碑已开启，进行查询
        response = self.get(api.format(project.id, main_milestone_state2_child1.id))
        self.assert_response_success(response)

    def test_save_common_project_milestone_state_info(self):
        """ 测试 通用项目里程碑信息保存和修改：【'调研', '实施调试', '项目验收'】"""
        api = '/api/v1/projects/{0}/project_milestone_states/{1}/save-research-info'

        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目x001')
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        # 分配项目负责人，同时开启需求论证里程碑
        is_dispatched, msg = project.dispatch(self.admin_staff)
        self.assertTrue(is_dispatched, msg)
        self.assertEqual(project.status, "SD")

        milestone_states = project.get_project_milestone_states()
        import os
        curr_path = os.path.dirname(__file__)
        with open(curr_path + '/data/upload_file_test.xlsx', 'wb+') as file_io:
            for index, item in enumerate(milestone_states):
                if item.milestone.title in ['调研', '实施调试', '项目验收']:
                    item.status = "DOING"
                    item.save()
                    item.cache()
                    file_name = 'upload_file_test%s.xlsx' % (index,)
                    upload_result = upload_file(
                        UploadedFile(file_io),
                        '%s' % (self.DOC_TEST_DIR,),
                        file_name
                    )
                    file_name = upload_result.get('name')
                    file_path = upload_result.get('path')
                    file = {'name': file_name, 'path': file_path}
                    cate_document = {'category': 'product', 'files': [file]}
                    cate_documents = [cate_document]
                    data_dict = {
                        'summary': '里程碑节点说明信息',
                        'cate_documents': cate_documents
                    }
                    response = self.post(api.format(project.id, item.id), data=data_dict)
                    self.assert_response_success(response)
                    saved_milestone_state = response.get('project_milestone_state')
                    self.assertIsNotNone(saved_milestone_state)
                    self.assertTrue(saved_milestone_state.get('is_saved'))
                    saved_file_path = saved_milestone_state.get('cate_documents')[0].get('files')[0].get('path')
                    self.assertEqual(saved_file_path, file_path)
                    self.assertEqual(
                        saved_milestone_state.get('cate_documents')[0].get('category'),
                        cate_document.get('category'))

    def test_save_project_milestone_state_plan_gathered_info(self):
        """测试方案保存/修改"""
        api_plan_gather_save = '/api/v1/projects/{0}/project_milestone_states/{1}/save-plan-gather-info'
        api_plan_gather_get = '/api/v1/projects/{0}/project_milestone_states/{1}/get-plan-gather-info'
        api_delete_plan = '/api/v1/projects/{0}/project_milestone_states/{1}/supplier_selection_plans/{2}'
        api_delete_plan_doc = '/api/v1/projects/{0}/project_milestone_states/{1}/supplier_selection_plans/{2}/documents/{3}'

        api_plan_argument_save = '/api/v1/projects/{0}/project_milestone_states/{1}/save-plan-argument-info'
        api_plan_argument_get = '/api/v1/projects/{0}/project_milestone_states/{1}/get-plan-argument-info'

        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目x002')
        if not self.get_default_flow():
            self.create_default_flow(self.organ)
        is_dispatched, msg = project.dispatch(self.admin_staff)
        self.assertTrue(is_dispatched, msg)
        self.assertEqual(project.status, "SD")

        # 保存方案收集信息
        create_plan_data = {
            "plan_list": [
                {
                    "supplier_name": "飞鸟科技有限公司001",
                    "total_amount": 100,
                    "remark": "备注：折扣10%",
                    "plan_files": [
                        {
                            "name": "supplier_selection_plan001",
                            "path": ("upload/project/document/%s/supplier_selection_plan001.txt" % (project.id, ))
                         },
                        {
                            "name": "supplier_selection_plan002",
                            "path": ("upload/project/document/%s/supplier_selection_plan002.txt" % (project.id,))
                        }
                    ],
                    "other_files": [
                        {
                            "name": "others001",
                            "path": ("upload/project/document/%s/supplier_selection_plan001.txt" % (project.id,))
                        },
                        {
                            "name": "others002",
                            "path": ("upload/project/document/%s/supplier_selection_plan001.txt" % (project.id,))
                        }
                    ]
                },
                {
                    "supplier_name": "飞鸟科技有限公司002",
                    "total_amount": 200,
                    "remark": "备注：折扣20%",
                    "plan_files": [
                        {
                            "name": "supplier_selection_plan003",
                            "path": ("upload/project/document/%s/supplier_selection_plan003.txt" % (project.id,))
                        },

                    ],
                    "other_files": [
                        {
                            "name": "others003",
                            "path": ("upload/project/document/%s/supplier_selection_plan003.txt" % (project.id,))
                        },
                    ]
                }
            ],
            "summary": "方案收集说明信息"
        }
        milestone_state_gather = self.startup_project_milestone_state(project, '方案收集')
        self.assertIsNotNone(milestone_state_gather)
        self.assertFalse(milestone_state_gather.modified_time)
        response = self.post(api_plan_gather_save.format(project.id, milestone_state_gather.id), data=create_plan_data)
        self.assert_response_success(response)
        saved_gather_state = response.get('project_milestone_state')
        self.assertIsNotNone(saved_gather_state)
        self.assertTrue(saved_gather_state.get('is_saved'))
        self.assertEqual(saved_gather_state.get('summary'), create_plan_data.get('summary'))
        self.assertEqual(saved_gather_state.get('milestone_title'), '方案收集')
        plans = saved_gather_state.get('supplier_selection_plans')
        self.assertIsNotNone(plans)
        self.assertEqual(plans[0].get('supplier_name'), create_plan_data.get('plan_list')[0].get('supplier_name'))
        self.assertEqual(plans[0].get('total_amount'), create_plan_data.get('plan_list')[0].get('total_amount'))
        self.assertEqual(plans[0].get('remark'), create_plan_data.get('plan_list')[0].get('remark'))
        self.assertIsNotNone(plans[0].get('plan_files')[0].get('id'))
        self.assertEqual(plans[0].get('plan_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('name'))
        self.assertEqual(plans[0].get('plan_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('path'))
        self.assertIsNotNone(plans[0].get('other_files')[0].get('id'))
        self.assertEqual(plans[0].get('other_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('name'))
        self.assertEqual(plans[0].get('other_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('path'))
        plan_id = plans[0].get('id')
        doc_id = plans[0].get('plan_files')[1].get('id')
        self.assertIsNotNone(doc_id)
        self.assertIsNotNone(plan_id)
        response = self.delete(api_delete_plan_doc.format(project.id,milestone_state_gather.id, plan_id, doc_id))
        self.assert_response_success(response)
        response = self.delete(api_delete_plan.format(project.id, milestone_state_gather.id, plans[1].get('id')))
        # self.assert_response_failure(response)
        self.assert_response_success(response)

        # 获取方案收集信息
        response = self.get(api_plan_gather_get.format(project.id, milestone_state_gather.id))
        self.assert_response_success(response)
        get_gather_state = response.get('project_milestone_state')
        self.assertIsNotNone(get_gather_state)
        self.assertIsNotNone(get_gather_state)
        self.assertEqual(get_gather_state.get('summary'), create_plan_data.get('summary'))
        self.assertEqual(get_gather_state.get('milestone_title'), '方案收集')
        plans = get_gather_state.get('supplier_selection_plans')
        self.assertIsNotNone(plans)
        self.assertEqual(len(plans), 1)
        self.assertEqual(len(plans[0].get('plan_files')), 1)
        self.assertEqual(plans[0].get('supplier_name'), create_plan_data.get('plan_list')[0].get('supplier_name'))
        self.assertEqual(plans[0].get('total_amount'), create_plan_data.get('plan_list')[0].get('total_amount'))
        self.assertEqual(plans[0].get('remark'), create_plan_data.get('plan_list')[0].get('remark'))
        self.assertIsNotNone(plans[0].get('plan_files')[0].get('id'))
        self.assertEqual(plans[0].get('plan_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('name'))
        self.assertEqual(plans[0].get('plan_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('path'))
        self.assertIsNotNone(plans[0].get('other_files')[0].get('id'))
        self.assertEqual(plans[0].get('other_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('name'))
        self.assertEqual(plans[0].get('other_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('path'))


        # 获取方案论证信息
        milestone_state_argument = self.startup_project_milestone_state(project, '方案论证')
        self.assertIsNotNone(milestone_state_argument)
        response = self.get(api_plan_argument_get.format(project.id, milestone_state_argument.id))
        self.assert_response_success(response)
        get_argument_state = response.get('project_milestone_state')
        self.assertIsNotNone(get_argument_state)
        self.assertIsNone(get_argument_state.get('summary'))
        self.assertEqual(get_argument_state.get('milestone_title'), '方案论证')
        self.assertEqual(get_argument_state.get('cate_documents'), [])
        plans = saved_gather_state.get('supplier_selection_plans')
        self.assertIsNotNone(plans)
        self.assertEqual(plans[0].get('supplier_name'), create_plan_data.get('plan_list')[0].get('supplier_name'))
        self.assertEqual(plans[0].get('total_amount'), create_plan_data.get('plan_list')[0].get('total_amount'))
        self.assertEqual(plans[0].get('remark'), create_plan_data.get('plan_list')[0].get('remark'))
        self.assertIsNotNone(plans[0].get('plan_files')[0].get('id'))
        self.assertEqual(plans[0].get('plan_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('name'))
        self.assertEqual(plans[0].get('plan_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('plan_files')[0].get('path'))
        self.assertIsNotNone(plans[0].get('other_files')[0].get('id'))
        self.assertEqual(plans[0].get('other_files')[0].get('name'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('name'))
        self.assertEqual(plans[0].get('other_files')[0].get('path'), create_plan_data.get('plan_list')[0].get('other_files')[0].get('path'))

        # 保存方案论证信息
        plan_argument_data = {
            "selected_plan_id": plans[0].get('id'),
            "cate_documents": [
                {
                    "category": "decision_argument",
                    "files": [
                        {
                            "name": "decision_argument001",
                            "path": "upload/project/document/%s/decision_argument001.txt" % (project.id,)
                        },
                        {
                            "name": "decision_argument002",
                            "path": "upload/project/document/%s/decision_argument002.txt" % (project.id,)
                        }
                    ]
                }
            ]
        }
        response = self.post(api_plan_argument_save.format(project.id, milestone_state_argument.id), data=plan_argument_data)
        self.assert_response_success(response)
        saved_argument_state = response.get('project_milestone_state')
        self.assertIsNotNone(saved_argument_state)
        self.assertTrue(saved_argument_state.get('is_saved'))
        saved_file_path = saved_argument_state.get('cate_documents')[0].get('files')[0].get('path')
        saved_file_name = saved_argument_state.get('cate_documents')[0].get('files')[0].get('name')

        self.assertEqual(saved_file_path, plan_argument_data.get('cate_documents')[0].get('files')[0].get('path'))
        self.assertEqual(saved_file_name, plan_argument_data.get('cate_documents')[0].get('files')[0].get('name'))

        self.assertEqual(saved_argument_state.get('cate_documents')[0].get('category'), plan_argument_data.get('cate_documents')[0].get('category'))
        plans = saved_argument_state.get('supplier_selection_plans')
        self.assertIsNotNone(plans)
        self.assertTrue(plans[0].get('selected'))
        self.assertEqual(plans[0].get('id'), plan_argument_data.get('selected_plan_id'))

    # def test_change_project_milestone_state(self):
    #
    #     api = '/api/v1/projects/{0}/change-project-milestone-state'
    # 
    #     self.login_with_username(self.user)
    #     project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目x004')
    #
    #     # 分配项目负责人，同时开启需求论证里程碑
    #     is_dispatched, msg = project.dispatch(self.admin_staff)
    #     self.assertTrue(is_dispatched, msg)
    #     self.assertEqual(project.status, "SD")
    #     default_flow = project.attached_flow
    #     main_milestone1 = default_flow.get_first_main_milestone()
    #     self.assertEqual(main_milestone1.title, "需求论证")
    #
    #     main_milestone2 = main_milestone1.next()
    #     self.assertEqual(main_milestone2.title, '圈定方案')
    #
    #     main_milestone2_child1 = main_milestone2.next()
    #     self.assertEqual(main_milestone2_child1.title, '调研')
    #     self.get_project_milestone_state(project, main_milestone2_child1)
    #     response = self.post(api.format(project.id), data={'project_milestone_state_id': main_milestone2_child1.id})
    #     self.assert_response_success(response)
    #     main_milestone2_child2 = main_milestone2_child1.next()
    #     self.assertEqual(main_milestone2_child2.title, '方案收集')
    #     main_milestone2_child3 = main_milestone2_child2.next()
    #     self.assertEqual(main_milestone2_child3.title, '方案论证')
    #
    #     main_milestone3 = main_milestone2_child3.next()
    #     self.assertEqual(main_milestone3.title, '采购管理')
    #
    #     main_milestone3_child1 = main_milestone3.next()
    #     self.assertEqual(main_milestone3_child1.title, '确定采购方式')
    #     main_milestone3_child2 = main_milestone3_child1.next()
    #     self.assertEqual(main_milestone3_child2.title, '启动采购')
    #     main_milestone3_child3 = main_milestone3_child2.next()
    #     self.assertEqual(main_milestone3_child3.title, '合同管理')
    #
    #     main_milestone4 = main_milestone3_child3.next()
    #     self.assertEqual(main_milestone4.title, '实施验收')
    #
    #     main_milestone4_child1 = main_milestone4.next()
    #     self.assertEqual(main_milestone4_child1.title, '到货')
    #     main_milestone4_child2 = main_milestone4_child1.next()
    #     self.assertEqual(main_milestone4_child2.title, '实施调试')
    #     main_milestone4_child3 = main_milestone4_child2.next()
    #     self.assertEqual(main_milestone4_child3.title, '项目验收')
    #     self.assertEqual(main_milestone4_child3.next(), None)

    def test_save_confirm_purchase(self):
        """
        api测试：测试确定采购方式保存接口
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/save-confirm-purchase-info'

        self.login_with_username(self.user)

        # 创建项目
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')

        # 判断是否存在默认流程
        default_flow = ProjectFlow.objects.filter(default_flow=True).first()
        if not default_flow:
            self.create_flow(self.organ)
        # 分配流程
        self.assertTrue(project.dispatch(self.admin_staff))

        milestone = Milestone.objects.filter(title='确定采购方式')
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone__in=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        # 改变确定采购方式项目里程碑的status
        project_milestone_state.status = PRO_MILESTONE_DOING
        project_milestone_state.save()

        # 初始化确定采购里程碑下相关数据
        init_data = {
            "summary": "确定采购方式里程碑测试用例",
            "purchase_method": "OPEN",
            "cate_documents": [
                {
                    "category": "contract",
                    "files": [
                        {
                            "name": "ceshi1.png",
                            "path": "upload/project/document/50051078/ceshi1.png",
                        },
                        {
                            "name": "ceshi2.png",
                            "path": "upload/project/document/50051078/ceshi2.png",
                        }
                    ]
                }
            ]
        }
        response = self.post(api.format(project.id, project_milestone_state.id), data=init_data)
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)
        self.assertTrue(project_milestone_state.get('is_saved'))
        self.assertIsNotNone(project_milestone_state.get('cate_documents'))
        self.assertEqual(project_milestone_state.get('purchase_method'), init_data.get('purchase_method'))
        self.assertEqual(project_milestone_state.get('summary'), init_data.get('summary'))
        cate_documents = project_milestone_state.get('cate_documents')
        for cate_document in cate_documents:
            files = []
            for file in cate_document.get('files'):
                file_data = {
                    "name": file.get('name'),
                    "path": file.get('path')
                }
                files.append(file_data)
                document = {
                    "category": cate_document.get('category'),
                    "files": files
                }
            self.assert_object_in_results(document, init_data.get('cate_documents'))

        self.assertEqual(len(project_milestone_state.get('cate_documents')),
                          len(init_data.get('cate_documents')))

    def test_get_confirm_purchase(self):
        """
        API测试：测试获取确定采购项目里程碑下的信息
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/get-confirm-purchase-info'

        self.login_with_username(self.user)

        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        # 查询是否存在默认流程
        default_flow = ProjectFlow.objects.get_default_flow()

        if not default_flow:
            self.create_flow(self.organ)

        self.assertTrue(project.dispatch(self.admin_staff))

        milestone = Milestone.objects.filter(title='确定采购方式', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        response = self.get(api.format(project.id, project_milestone_state.id))
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)
        cate_documents = project_milestone_state.get('cate_documents')
        if not cate_documents:
            cate_documents = None
        self.assertIsNone(cate_documents)

    def test_save_startup_purchase_info(self):
        """
        API测试:启动采购项目里程碑保存接口测试
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/save-startup-purchase-info'

        self.login_with_username(self.user)

        # 创建项目
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        # 获取默认流程
        default_flow = ProjectFlow.objects.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        # 获取milestone
        milestone = Milestone.objects.filter(title='启动采购', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)

        project_milestone_state.status = PRO_MILESTONE_DOING
        project_milestone_state.save()

        init_data = {
            "summary": "启动采购项目里程碑测试用例",
            "cate_documents": [
                {
                    "category": "bidding_doc",
                    "files": [
                        {
                            "name": "招标文件.txt",
                            "path": "%s%s%s" % ("upload/project/document/", str(project.id), "/招标文件.txt")
                        }
                    ]
                },
                {
                    "category": "purchase_plan",
                    "files": [
                        {
                            "name": "采购计划.txt",
                            "path": "%s%s%s" % ("upload/project/document/", str(project.id), "/采购计划.txt")
                        }
                    ]
                },
                {
                    "category": "tender_doc",
                    "files": [
                        {
                            "name": "投标文件.text",
                            "path": "%s%s%s" % ("upload/project/document/", str(project.id), "/投标文件.txt")
                        },
                        {
                            "name": "投标文件1.text",
                            "path": "%s%s%s" % ("upload/project/document/", str(project.id), "/投标文件1.txt")
                        }
                    ]
                }
            ]
        }
        response = self.post(api.format(project.id, project_milestone_state.id), data=init_data)
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)
        self.assertTrue(project_milestone_state.get('is_saved'))
        self.assertIsNotNone(project_milestone_state.get('summary'))
        self.assertIsNotNone(project_milestone_state.get('cate_documents'))
        cate_documents = project_milestone_state.get('cate_documents')
        for cate_document in cate_documents:
            files = []
            for file in cate_document.get('files'):
                file_data = {
                    "name": file.get('name'),
                    "path": file.get('path')
                }
                files.append(file_data)
                document = {
                    "category": cate_document.get('category'),
                    "files": files
                }
            self.assert_object_in_results(document, init_data.get('cate_documents'))

        self.assertEqual(len(project_milestone_state.get('cate_documents')), len(init_data.get('cate_documents')))

    def test_get_startup_purchase_info(self):
        """
        API测试: 测试获取启动采购项目里程碑下相关信息
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/get-startup-purchase-info'

        self.login_with_username(self.user)
        # 创建项目
        project = self.create_project(self.admin_staff, self.dept, project_cate="SW", title='测试项目')

        default_flow = ProjectFlow.objects.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='启动采购', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)

        response = self.get(api.format(project.id, project_milestone_state.id))
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project_milestone_state'))

    def test_save_purchase_contract_info(self):
        """
        API测试: 合同管理项目里程碑节点下的保存操作接口
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/save-purchase-contract-info'
        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')

        default_flow = ProjectFlow.objects.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='合同管理', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        project_milestone_state.status = PRO_MILESTONE_DOING
        project_milestone_state.save()
        init_data = {
            "contract_no": "BJ20180927",
            "title": "测试合同管理",
            "signed_date": "2018-09-27",
            "seller_contact": "乙方联系人",
            "seller": "乙方单位",
            "seller_tel": "13453453456",
            "buyer_contact": "甲方联系人",
            "total_amount": 1231221,
            "delivery_date": "2018-09-28",
            "contract_devices": [
                {
                    "id": None,
                    "name": "测试系统1",
                    "producer": "厂商1",
                    "supplier": "供应商",
                    "planned_price": 123000.0,
                    "real_price": 123000,
                    "num": 2,
                    "real_total_amount": 246000
                },
                {
                    "id": None,
                    "name": "测试系统2",
                    "producer": "厂商2",
                    "supplier": "供应商",
                    "planned_price": 123000.0,
                    "real_price": 12000,
                    "num": 2,
                    "real_total_amount": 24000
                }
            ],
            "summary": "测试合同管理项目里程碑保存操作",
            "cate_documents": [
                {
                    "category": "contract",
                    "files": [
                        {
                            "name": "合同1",
                            "path": "%s%s%s" % ("upload/project/document/", project.id, "/合同1")
                        }
                    ]
                },
                {
                    "category": "others",
                    "files": [
                        {
                            "name": "其他资料1",
                            "path": "%s%s%s" % ("upload/project/document/", project.id, "其他资料1")
                        },
                        {
                            "name": "其他资料2",
                            "path": "%s%s%s" % ("upload/project/document/", project.id, "其他资料2")
                        }
                    ]
                }
            ]
        }

        response = self.post(api.format(project.id, project_milestone_state.id), data=init_data)
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)
        self.assertTrue(project_milestone_state.get('is_saved'))
        self.assertIsNotNone(project_milestone_state.get('purchase_contract'))
        self.assertIsNotNone(project_milestone_state.get('purchase_contract').get('contract_devices'))
        self.assertEqual(len(project_milestone_state.get('purchase_contract').get('contract_devices')), 2)
        self.assertIsNotNone(project_milestone_state.get('cate_documents'))
        self.assertEqual(len(project_milestone_state.get('cate_documents')), 2)
        for cate_document in project_milestone_state.get('cate_documents'):
            self.assertIsNotNone(cate_document)
            if cate_document.get('category') == 'contract':
                self.assertEqual(len(cate_document.get('files')), 1)
            if cate_document.get('category') == 'others':
                self.assertEqual(len(cate_document.get('files')), 2)

    def test_get_purchase_contract_info(self):
        """
        API测试: 获取合同管理项目里程碑下的相关信息
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/get-purchase-contract-info'
        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='合同管理', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(milestone=milestone, project=project).first()
        self.assertIsNotNone(project_milestone_state)
        response = self.get(api.format(project.id, project_milestone_state.id))
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project_milestone_state'))

    def test_save_take_delivery_info(self):
        """
        API测试: 到货项目里程碑操作API接口测试
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/save-take-delivery-info'
        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')

        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='到货', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        project_milestone_state.status = PRO_MILESTONE_DOING
        project_milestone_state.save()
        init_data = {
            "served_date": "2018-10-10",
            "delivery_man": "龚怀前",
            "contact_phone": "13499999999",
            "summary": "到货项目里程碑下保存操作",
            "cate_documents": [
                {
                    "category": "delivery_note",
                    "files": [
                        {
                            "name": "送货单",
                            "path": "%s%s%s" % ("upload/project/document/", project.id, "/送货单")
                        }
                    ]
                }
            ]
        }
        response = self.post(api.format(project.id, project_milestone_state.id), data=init_data)
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)
        self.assertTrue(project_milestone_state.get('is_saved'))
        cate_documents = project_milestone_state.get('cate_documents')
        self.assertIsNotNone(cate_documents)
        self.assertEqual(len(cate_documents), len(init_data.get('cate_documents')))
        self.assertEqual(len(cate_documents), 1)
        cate_document = cate_documents[0]
        self.assertIsNotNone(cate_document)
        self.assertEqual(cate_document.get('category'), "delivery_note")
        self.assertIsNotNone(cate_document.get('files'))
        self.assertEqual(len(cate_document.get('files')), 1)
        file = cate_document.get('files')[0]
        self.assertIsNotNone(file)
        self.assertEqual(file.get('name'), "送货单")
        self.assertEqual(file.get('path'), "%s%s%s" % ("upload/project/document/", project.id, "/送货单"))

    def test_get_take_delivery_info(self):
        """
        API测试: 获取到货项目里程碑下的信息
        """
        api = '/api/v1/projects/{}/project_milestone_states/{}/get-take-delivery-info'
        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='到货', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        response = self.get(api.format(project.id, project_milestone_state.id))
        self.assert_response_success(response)
        project_milestone_state = response.get('project_milestone_state')
        self.assertIsNotNone(project_milestone_state)

    def test_delete_contract_device(self):
        """
        API测试：测试删除合同中合同设备接口测试
        """
        api = '/api/v1/projects/{}/purchase_contracts/{}/contract_devices/{}'
        self.login_with_username(self.user)
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        default_flow = self.get_default_flow()
        if not default_flow:
            self.create_flow(self.organ)
        self.assertTrue(project.dispatch(self.admin_staff))
        milestone = Milestone.objects.filter(title='合同管理', flow__default_flow=True).first()
        self.assertIsNotNone(milestone)
        project_milestone_state = ProjectMilestoneState.objects.filter(project=project, milestone=milestone).first()
        self.assertIsNotNone(project_milestone_state)
        purchase_contract = self.create_purchase_contract(project_milestone_state)
        self.assertIsNotNone(purchase_contract)
        contract_devices = purchase_contract.contract_devices.all()
        self.assertIsNotNone(contract_devices)
        contract_device = contract_devices[0]
        self.assertIsNotNone(contract_device)
        response = self.delete(api.format(project.id, purchase_contract.id, contract_device.id))
        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)
        new_contract_devices = purchase_contract.contract_devices.all()
        self.assert_object_not_in_results(contract_device, new_contract_devices)
