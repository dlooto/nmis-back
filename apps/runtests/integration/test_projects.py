# coding=utf-8
#
# Created by junn, on 2018/6/11
#

# 

import logging

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

        # 仅项目管理者(医院管理员, 项目分配者)及项目提交者可以查看项目详情
        data = {
            "hospital_id": self.organ.id,
        }
        project = self.create_project(self.admin_staff, self.dept, title="新项目")
        response = self.get(self.single_project_api.format(project.id), data=data)
        self.assert_response_success(response)
        self.assertIsNotNone(response.get("project"))
        self.assertEquals(response.get("project").get('title'), project.title)

        # TODO: 增加对接口请求权限的验证...

    def test_project_update(self):
        """
        修改项目
        """

        self.login_with_username(self.user)

        old_project = self.create_project(self.admin_staff, self.dept, title="旧项目名")
        old_device = old_project.get_ordered_devices()[0]

        project_data = {
            "hospital_id": self.organ.id,
            "project_title": "新的项目名称",
            "purpose": "修改后的用途说明",
        }

        response = self.put(self.single_project_api.format(old_project.id), data=project_data)
        self.assert_response_success(response)
        new_project = response.get('project')
        self.assertIsNotNone(new_project)
        self.assertEquals(new_project.get('title'), project_data['project_title'])

    def test_project_create(self):
        """
        api测试: 创建项目申请
        """

        self.login_with_username(self.user)

        project_data = {
            "hospital_id": self.organ.id,
            "project_title": "牛逼项目1",
            "purpose": "牛逼的不能为外人说道的目标",
            "creator_id": self.admin_staff.id,
            "related_dept_id": self.admin_staff.dept.id,
            "ordered_devices": [
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
            ]
        }

        response = self.post(self.project_create_api, data=project_data)
        self.assert_response_success(response)

        result_project = response.get('project')
        self.assertIsNotNone(result_project)
        self.assertEquals(project_data['project_title'], result_project.get('title'))
        self.assertEquals(
            len(result_project.get('ordered_devices')), len(project_data.get('ordered_devices'))
        )
        self.assert_object_in_results(project_data.get('ordered_devices')[0],
                                      result_project.get('ordered_devices'))

    def test_my_project_list(self):
        """
        api测试：我的项目列表(带筛选)api接口测试
        """
        api = "/api/v1/projects/my-projects"

        self.login_with_username(self.user)
        for index in range(0, 5):
            project = self.create_project(self.admin_staff, self.dept,
                                          title='测试项目_{}'.format(self.get_random_suffix()))

        project_data = {
            'organ_id': self.organ.id,
            'lower_expired_date': yesterday(),
            'upper_expired_date': now(),
            'pro_status': 'PE',
            'pro_title_leader': '测试',
            'creator_id': self.admin_staff.id,
            'current_stone_id': '',
            'type': 'my_projects'
        }

        response = self.get(api, data=project_data)
        self.assert_response_success(response)

        self.assertIsNotNone(response.get('projects'))
        self.assertEquals(len(response.get('projects')), 5)
        self.assert_object_in_results(
            {'creator_id': self.admin_staff.id}, response.get('projects')
        )

    def test_undispatched_project_list(self):
        """
        api测试：待分配项目api接口测试
        """
        api = "/api/v1/projects/allot-projects"

        self.login_with_username(self.user)
        # 创建一个待分配项目
        project1 = self.create_project(self.admin_staff, self.dept, title='我是待分配项目1')
        project2 = self.create_project(self.admin_staff, self.dept, title='我是待分配项目2')

        project_data = {
            'organ_id': self.organ.id,
            'type': 'undispatch'
        }
        response = self.get(api, data=project_data)

        self.assert_response_success(response)
        results = response.get('projects')
        self.assertIsNotNone(results)
        self.assertEquals(len(results), 2)
        self.assert_object_in_results({'title': project1.title}, results)

    def test_project_dispatch(self):
        """
        API测试：分配项目给负责人接口测试
        """
        api = '/api/v1/projects/{}/dispatch'
        self.login_with_username(self.user)
        # 创建项目
        project_plan = self.create_project(self.admin_staff, self.dept, title='待分配项目')

        # 创建项目流程
        project_flow = self.create_flow(self.organ)

        data = {
            'performer_id': self.admin_staff.id,
            'flow_id': project_flow.id,
            'expired_time': str(tomorrow())
        }

        response = self.post(api.format(project_plan.id), data=data)
        self.assert_response_success(response)
        project = response.get('project')
        self.assertIsNotNone(project.get('performer_id'))
        self.assertIsNotNone(project.get('attached_flow_id'))
        self.assertEquals(project_plan.id, project.get('id'))
