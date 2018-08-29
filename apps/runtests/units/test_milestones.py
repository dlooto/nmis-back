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
        测试: 项目分配(分配项目负责人，分配默认流程，项目直接进入需求论证里程碑)
        """
        self.assertTrue(self.project.is_unstarted())

        success = self.project.dispatch(self.performer)
        self.assertTrue(success)
        self.assertFalse(self.project.is_unstarted())  # 分配后项目后状态发生改变(变成已启动状态)
        self.assertIsNotNone(self.project.performer)

    def test_project_redispatch(self):
        """
        测试: 项目重新分配(不改变项目的里程碑状态，只改变项目负责人信息)
        """
        self.assertTrue(self.project.is_unstarted())
        # 先分配项目负责人
        dispatch_success = self.project.dispatch(self.performer)
        self.assertTrue(dispatch_success)
        self.assertFalse(self.project.is_unstarted())
        self.assertIsNotNone(self.project.performer)

        # 重新分配项目负责人
        redispatch_success = self.project.redispatch(self.admin_staff)
        self.assertTrue(redispatch_success)
        self.assertFalse(self.project.is_unstarted())
        self.assertEquals(self.admin_staff, self.project.performer)

    def test_change_milestone(self):
        """
        测试: 变更项目里程碑项
        """
        # 分配负责人
        self.assertTrue(
            self.project.dispatch(self.performer)
        )
        # 启动项目
        self.assertTrue(
            self.project.startup(
                assistant=self.admin_staff,
                flow=self.flow,
                expired_time=times.tomorrow()
            )
        )

        self.assertEquals(self.project.current_stone, self.flow.get_first_milestone())

        # new_milestone = self.project.current_stone
        # success, msg = self.project.change_milestone(new_milestone)
        # self.assertFalse(success)

        new_milestone = self.project.current_stone.next()
        success, msg = self.project.change_milestone(new_milestone, done_sign='UN')
        self.assertTrue(success)
        self.assertEquals(self.project.current_stone, new_milestone)
        self.assertTrue(self.project.contains_recorded_milestone(new_milestone))


