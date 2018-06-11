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

    dept_update_api = '/api/v1/hospitals/{0}/departments/{1}'

    def test_department_update(self):
        """
        测试科室信息修改api
        """

        self.login_with_username(self.user)

        dept_data = {
            "name": "新科室1",
            "contact": "13512345678",
            "desc": "这是个新的科室",
            "attri": "ME"
        }

        response = self.put(
            self.dept_update_api.format(self.organ.id, self.admin_staff.dept_id),
            data=dept_data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))
        self.assertEquals(dept_data['name'], response.get('dept').get('name'))


class StaffUpdateTestCase(BaseTestCase):

    staff_update_api = '/api/v1/hospitals/{0}/staffs/{1}'

    @skip
    def test_staff_update(self):
        """
        测试员工信息修改
        """
        data = {
            'username': 'abc_test123', 'password': 'x111111',
            'email': 'test_email@nmis.com'
        }

        a_staff = self.create_staff(None, self.organ)
        a_staff.set_group(self.organ.get_admin_group())

        data.update({'authkey': 'username'})
        resp = self.post(self.login_api, data=data)

        self.assert_response_success(resp)

    @skip
    def test_staff_get(self):
        pass

