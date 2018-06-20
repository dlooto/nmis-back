# coding=utf-8
#
# Created by junn, on 2018/6/11
#

import logging
import random
from unittest import skip

from nmis.hospitals.models import Staff
from runtests import BaseTestCase

logs = logging.getLogger(__name__)


class DepartmentApiTestCase(BaseTestCase):
    """
    科室相关测试API
    """

    dept_create_api = '/api/v1/hospitals/{0}/departments/create'
    # 单个科室增删查API
    dept_single_operation_api = '/api/v1/hospitals/{0}/departments/{1}'
    dept_list = '/api/v1/hospitals/{0}/departments'

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
            self.dept_single_operation_api.format(self.organ.id, self.admin_staff.dept_id),
            data=dept_data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))
        self.assertEquals(dept_data['name'], response.get('dept').get('name'))

    def test_department_create(self):
        """
        测试创建科室api
        """
        self.login_with_username(self.user)

        dept_data = {
            "name": "测试科室",
            "contact": "15884948954",
            "desc": "用于测试",
            "attri": "SU",
            "organ": self.organ
        }
        response = self.raw_post(
            self.dept_create_api.format(self.organ.id),
            data=dept_data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))

    def test_department_detail(self):
        """
        测试获取科室详细信息api
        """
        self.login_with_username(self.user)

        response = self.get(
            self.dept_single_operation_api.format(self.organ.id, self.admin_staff.dept_id),
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))

    def test_department_del(self):
        """
        测试删除科室api
        """

        self.login_with_username(self.user)

        resp = self.delete(
            self.dept_single_operation_api.format(self.organ.id, self.admin_staff.dept_id)
        )

        self.assert_response_success(resp)
        self.assertIsNone(resp.get('dept'))
        # self.assertNotEquals(resp.get('msg'), '操作成功')

    def test_departments_list(self):
        """
        测试科室列表
        """
        self.login_with_username(self.user)

        response = self.get(
            self.dept_list.format(self.organ.id)
        )

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))


class StaffsPermChangeTestCase(BaseTestCase):
    """
    测试staff权限分配相关API
    """
    staffs_permChange_api = '/api/v1/hospitals/{0}/staffs/change_permission'
    staffs_list_api = '/api/v1/hospitals/{0}/staffs'
    group_list_api = "/api/v1/hospitals/{0}/groups"

    def test_staffs_permChange(self):
        """
        测试管理员给员工非配权限
        """

        self.login_with_username(self.user)
        # 初始化staff相应数据
        data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        # 创建部门
        dept = self.create_department(self.organ)
        # 创建员工同时创建一个用户账号
        self.create_completed_staff(self.organ, dept, '测试01', **data)
        response = self.get(
            self.staffs_list_api.format(self.organ.id)
        )
        resp = self.get(
            self.group_list_api.format(self.organ.id)
        )
        # self.assertIsNone(self)
        if not self.assert_response_success(response) and \
                not self.assert_response_success(resp):
            staffs_list = response.get('staff')
            group_list = resp.get('group')
            staffs_id_list = []
            group_id_list = []
            for index in range(len(staffs_list)):
                staffs_id_list.append(staffs_list[index].get('id'))
            for index in range(len(group_list)):
                group_id_list.append(group_list[index].get('id'))
            group_id = random.sample(group_id_list, 1)[0]
            staffs_id_str = ",".join('%s' % staff_id for staff_id in staffs_id_list)
            data = {
                'perm_group_id': group_id,
                'staffs': staffs_id_str
            }

            # self.assertIsNone(staffs_list)
            response = self.put(
                self.staffs_permChange_api.format(self.organ.id),
                data=data
            )

            self.assert_response_success(response)


class StaffAPITestCase(BaseTestCase):

    staff_create_api = '/api/v1/hospitals/{0}/staffs/create'
    staff_update_get_delete_api = '/api/v1/hospitals/{0}/staffs/{1}'

    def test_staff_create(self):
        """
        测试新增员工信息
        :return:
        """
        self.login_with_username(self.user)

        new_staff_data = {
            'username': 'add_user_test001',
            'password': '123456',
            'staff_name': 'add_zhangsan_test001',
            'staff_title': 'zhuzhiyishi',
            'contact_phone': '15822012220',
            'email': 'zhangshang@test.com',
            'dept_id': self.admin_staff.dept_id,
            'group_id': '',
        }

        response = self.post(
            self.staff_create_api.format(self.organ.id),
            data=new_staff_data
        )
        self.assert_response_success(response)
        # self.assert_response_failure(response)  #暴露数据
        self.assertIsNotNone(response.get("staff"))
        self.assertIsNotNone(response.get("staff").get('staff_name'))
        self.assertEquals(response.get('staff').get('staff_name'), new_staff_data['staff_name'])

    def test_staff_get(self):
        """
        测试获取员工详细信息
        :return:
        """
        self.login_with_username(self.user)
        # new_staff = self.create_completed_staff(self.organ, self.dept, 'test001')
        response = self.get(
            self.staff_update_get_delete_api.format(
                self.organ.id,
                self.admin_staff.id,
            )
        )
        self.assert_response_success(response)
        #self.assert_response_failure(response)
        self.assertIsNotNone(response.get('staff'), '没获取到员工信息')
        self.assertIsNotNone(response.get('staff').get('staff_name'), '没获取到员工姓名')
        self.assertEquals(response.get('staff').get('staff_name'), self.admin_staff.name)

    def test_staff_update(self):
        """
        测试更新员工信息
        :return:
        """
        self.login_with_username(self.user)

        update_staff_data = {
            'username': 'add_user_test001',
            'password': '123456',
            'staff_name': 'add_zhangsan_test001',
            'staff_title': 'zhuzhiyishi',
            'contact_phone': '19822012220',
            'email': 'zhangshang@test.com',
            'dept_id': self.admin_staff.id,
            'group_id': '',
        }
        response = self.put(
            self.staff_update_get_delete_api.format(
                self.organ.id,
                self.admin_staff.id,
            )
        )
        self.assert_response_success(response)
        #self.assert_response_failure(response)
        self.assertIsNotNone(response.get('staff'), '没获取到修改后的员工信息')
        self.assertIsNotNone(response.get('staff').get('staff_name'), '没有获取到修改后的员工姓名')
        self.assertEqual(response.get('staff').get('staff_name'), self.admin_staff.name)

    def test_staff_delete(self):
        """
        测试删除员工信息
        :return:
        """

        self.login_with_username(self.user)
        response = self.delete(
            self.staff_update_get_delete_api.format(self.organ.id, self.admin_staff.id)
        )

        self.assert_response_success(response)
        self.assert_response_failure()


