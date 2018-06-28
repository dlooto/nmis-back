# coding=utf-8
#
# Created by junn, on 2018/6/26
#

# 

import logging

from runtests import BaseTestCase
from runtests.common.mixins import ProjectPlanMixin, MILESTONES
from utils import times

logs = logging.getLogger(__name__)


class ProjectFlowTestCase(BaseTestCase, ProjectPlanMixin):
    """
    项目流程测试相关
    """

    def test_project_flow_create(self):
        """
        测试: 创建项目流程
        """
        api = "/api/v1/projects/flows/create"

        flow_data = {
            "organ_id": self.organ.id,
            "flow_title": "测试流程_{}".format(self.get_random_suffix()),
            "milestones": MILESTONES
        }

        self.login_with_username(self.user)
        response = self.post(api, data=flow_data)
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('flow'))
        self.assertEquals(len(response.get('flow').get("milestones")), len(MILESTONES))

    def test_project_milestone_change(self):
        """
        api测试: 变更项目里程碑状态
        """

        api = '/api/v1/projects/{}/change-milestone'

        project = self.create_project(self.admin_staff, self.dept)
        performer = self.create_completed_staff(self.organ, self.dept, name="项目负责人_接口测试")
        project.performer = performer
        project.save()

        flow = self.create_flow(self.organ)

        # 启动项目
        self.assertTrue(
            project.dispatch(performer, **{"flow": flow, "expired_time": times.now()})
        )
        new_milestone = project.current_stone.next()
        self.assertIsNotNone(new_milestone)

        self.login_with_username(performer.user)
        response = self.post(api.format(project.id),
                  data={"milestone_id": new_milestone.id})
        self.assert_response_success(response)

        result_project = response.get("project")
        self.assertEquals(new_milestone.id, result_project.get("current_stone_id"))
        self.assertTrue(project.contains_recorded_milestone(new_milestone))

        # clear data
        performer.user.clear_cache()
        performer.clear_cache()

    def test_project_flow_update(self):
        """
        api测试：变更项目流程
        """

        # 测试正常更改
        api = '/api/v1/projects/flows/{}'

        self.login_with_username(self.user)
        flow = self.create_flow(self.organ)

        response = self.put(
            api.format(flow.id),
            data={'organ_id': self.organ.id, 'flow_title': '流程名称UpdateTest'}
        )
        self.assert_response_success(response)
        self.assertEqual('流程名称UpdateTest', response.get('flow')['title'])

        # 测试流程已经被使用
        project = self.create_project(creator=self.admin_staff, dept=self.dept, title="设备采购Test", )
        project.dispatch(self.admin_staff, **{"flow": flow, "expired_time": times.now()})
        response2 = self.put(
            api.format(flow.id),
            data={'organ_id': self.organ.id, 'flow_title': '流程名称UpdateTest'}
        )
        self.assert_response_form_errors(response2)
        self.assertEqual(response2['errors']['flow_id'], '流程已经在使用中，不能修改')

    def test_project_flow_delete(self):
        """
        api测试：删除项目流程
        """
        api = '/api/v1/projects/flows/{}'

        self.login_with_username(self.user)
        flow = self.create_flow(self.organ)

        response = self.delete(api.format(flow.id))
        self.assert_response_success(response)
