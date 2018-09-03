# coding=utf-8
#
# Created by junn, on 2018/6/11
#

# 

import logging

from nmis.projects.consts import (PRO_HANDING_TYPE_AGENT, PRO_STATUS_STARTED,
                                  PRO_CATE_SOFTWARE, PRO_CATE_HARDWARE,
                                  PRO_STATUS_OVERRULE, PRO_OPERATION_OVERRULE,
                                  PRO_OPERATION_PAUSE, PRO_STATUS_PAUSE, PRO_STATUS_DONE)
from runtests import BaseTestCase
from runtests.common.mixins import ProjectPlanMixin
from utils.times import now, yesterday, tomorrow

logs = logging.getLogger(__name__)


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
        self.assertEquals(response.get("project").get('title'), project.title)

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
                "purpose": "有卵用"
            },
            {
                "name": "牛逼的系统",
                "purpose": "有卵用"
            }
        ]
        software_updated_devices = [
            {
                "id": software_project.get_software_devices()[0].id,
                "name": "修改系统名",
                "purpose": "修改系统用途"
            },
            {
                "id": software_project.get_software_devices()[1].id,
                "name": "修改的系统名",
                "purpose": "修改的系统用途"
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
        self.assertEquals(new_project.get('title'), project_base_data['project_title'])
        self.assertEqual(new_project.get('handing_type'), project_base_data['handing_type'])
        self.assertEquals(new_project.get('performer_id'), new_project.get('creator_id'))
        devices = new_project['hardware_devices']
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
        self.assertEquals(len(hardware_devices), 4)
        self.assertEquals(len(software_devices), 4)

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
        self.assertEquals(response.get('code'), 10000)

        # 测试项目被使用，不能删除
        new_project = self.create_project(self.admin_staff, self.dept, title='新的测试项目')
        new_project.performer = self.admin_staff
        new_project.save()

        response2 = self.delete(
            self.single_project_api.format(new_project.id)
        )

        self.assert_response_failure(response2)
        self.assertEquals(response2.get('code'), 0)
        self.assertEquals(response2.get('msg'), '项目已被分配，无法删除')

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
                    "purpose": "单点登录"
                }
            ]
        }

        response = self.post(self.project_create_api, data=project_data)
        self.assert_response_success(response)

        result_project = response.get('project')
        self.assertIsNotNone(result_project)
        self.assertEquals(project_data['project_title'], result_project.get('title'))
        self.assertEquals(project_data['handing_type'], result_project.get('handing_type'))

        self.assertEquals(
            len(result_project.get('hardware_devices')), len(project_data.get('hardware_devices'))
        )
        self.assertEquals(
            len(result_project.get('software_devices')), len(project_data.get('software_devices'))
        )
        self.assert_object_in_results(project_data.get('hardware_devices')[0],
                                      result_project.get('hardware_devices'))
        self.assertEquals(project_data.get('pro_type'), result_project.get('project_cate'))

        # 测试转交办理、医疗器械设备项目申请
        pro2_data = project_data
        pro2_data['handing_type'] = PRO_HANDING_TYPE_AGENT
        pro2_data['pro_type'] = PRO_CATE_HARDWARE

        resp2 = self.post(self.project_create_api, data=pro2_data)
        self.assert_response_success(resp2)
        pro2 = resp2.get('project')
        self.assertIsNotNone(pro2)
        self.assertEquals(pro2_data['handing_type'], pro2.get('handing_type'))
        self.assertIsNone(pro2.get('performer_id'))
        self.assertEquals(pro2_data.get('pro_type'), pro2.get('project_cate'))
        self.assertEquals(len(pro2_data.get('hardware_devices')), len(pro2.get('hardware_devices')))
        self.assertEquals(len(pro2.get('software_devices')), 0)

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
        self.assertEquals(len(response.get('projects')), 4)
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
        self.assertEquals(len(results), 2)
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
        self.assertEquals(len(response.get('projects')), 5)
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
        self.assertEquals(len(response.get('projects')), 5)
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

        # 分配项目
        success = project_plan.dispatch(self.admin_staff)
        self.assertTrue(success)
        self.assertIsNotNone(project_plan.performer)
        self.assertEquals(self.admin_staff.id, project_plan.performer.id)

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
        self.assertEquals(staff.id, project.get('performer_id'))

    def test_project_dispatch(self):
        """
        API测试：分配项目负责人（分配默认流程，改变项目状态，项目直接进入默认流程的需求论证里程碑）
        """
        api = '/api/v1/projects/{}/dispatch'

        self.login_with_username(self.user)

        # 创建项目
        project_plan = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='新建项目申请')

        data = {
            'performer_id': self.admin_staff.id,
        }
        response = self.put(api.format(project_plan.id), data=data)
        self.assert_response_success(response)
        project = response.get('project')
        self.assertIsNotNone(project.get('performer_id'))
        self.assertEquals(project_plan.id, project.get('id'))
        self.assertEquals(self.admin_staff.id, project.get('performer_id'))

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
        self.assertEquals(len(projects), 3)
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
        self.assertEquals(len(projects), 3)

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
        self.assertEquals(response.get('project').get('status'), PRO_STATUS_OVERRULE)

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
        self.assertEquals(len(response.get('projects')), 4)

    def test_pause_project(self):
        """
        API测试:测试项目负责人挂起项目
        """
        api = '/api/v1/projects/{}/pause'

        self.login_with_username(self.user)

        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试挂起项目')

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
        self.assertEquals(response.get('project').get('status'), PRO_STATUS_PAUSE)

    def test_cancel_pause_project(self):
        """
        API测试:测试项目负责人取消项目挂起
        """
        api = '/api/v1/projects/{}/cancel-pause'

        self.login_with_username(self.user)
        # 创建测试项目
        project = self.create_project(self.admin_staff, self.dept, project_cate='SW', title='测试项目')
        # 创建测试项目默认流程
        defalut_flow = self.create_flow(self.organ)
        # 分配项目
        self.assertTrue(project.dispatch(self.admin_staff))

        response = self.put(api.format(project.id))

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('project'))
        self.assertEquals(response.get('project').get('status'), PRO_STATUS_STARTED)

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

        defalut_flow = self.create_flow(self.organ)
        # 分配项目负责人
        self.assertTrue(project.dispatch(self.admin_staff))
        data = {
            'assistant_id': staff.id
        }
        response = self.put(api.format(project.id), data=data)

        self.assert_response_success(response)
        self.assertEquals(response.get('code'), 10000)

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
        self.assertEquals(response.get('projects')[0].get('assistant_id'), self.admin_staff.id)