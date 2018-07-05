# coding=utf-8
#
# Created by junn, on 2018/6/25
#

# 

import logging

from runtests import BaseTestCase
from runtests.common.mixins import ProjectPlanMixin
from utils import times

logs = logging.getLogger(__name__)


class ProjectTestCase(BaseTestCase, ProjectPlanMixin):

    def setUp(self):
        super(ProjectTestCase, self).setUp()
        self.project = self.create_project(self.admin_staff, self.dept)
        self.performer = self.create_completed_staff(self.organ, self.dept, name="项目负责人x")

        self.flow = self.create_flow(self.organ)

    def test_project_dispatch(self):
        """
        测试: 项目分配
        :return:
        """
        self.assertTrue(self.project.is_unstarted())

        success = self.project.dispatch(self.performer)
        self.assertTrue(success)
        # self.assertFalse(self.project.is_unstarted()) # 分配后项目进入启动状态
        # self.assertEquals(self.project.current_stone, self.flow.get_first_milestone())

    def test_change_milestone(self):
        """
        测试: 变更项目里程碑项
        """
        self.assertTrue(
            self.project.dispatch(self.performer)
        )
        # self.assertEquals(self.project.current_stone, self.flow.get_first_milestone())

        # new_milestone = self.project.current_stone
        # success, msg = self.project.change_milestone(new_milestone)
        # self.assertFalse(success)

        # # new_milestone = self.project.current_stone.next()
        # success, msg = self.project.change_milestone(new_milestone)
        # self.assertTrue(success)
        # self.assertEquals(self.project.current_stone, new_milestone)
        # self.assertTrue(self.project.contains_recorded_milestone(new_milestone))


