# coding=utf-8
#
# Created by junn, on 2018/6/11
#

# 

import logging
from unittest import skip

from runtests import BaseTestCase

logs = logging.getLogger(__name__)


class DepartmentApiTestCase(BaseTestCase):

    project_create_api = '/api/v1/projects/create'

    def test_project_create(self):
        """
        api测试: 创建项目申请
        """

        self.login_with_username(self.user)

        project_data = {
            "hospital_id": self.organ.id,
            "project_title": "牛逼项目1",
            "purpose": "牛逼的不能为外人说道的目的",
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


