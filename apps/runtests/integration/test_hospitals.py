# coding=utf-8
#
# Created by junn, on 2018/6/11
#

import logging
import random
from unittest import skip

from django.core.files.uploadedfile import UploadedFile
from django.http.multipartparser import FILE
from django.test import Client

from nmis.hospitals.models import Staff
from runtests import BaseTestCase
from settings import FIXTURE_DIRS

logs = logging.getLogger(__name__)


class DepartmentApiTestCase(BaseTestCase):
    """
    科室相关测试API
    """

    dept_create_api = '/api/v1/hospitals/{0}/departments/create'
    dept_single_operation_api = '/api/v1/hospitals/{0}/departments/{1}'  # 单个科室增删查API
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
        # 创建科室
        dept = self.create_department(self.organ, dept_name='测试科室')

        resp = self.delete(
            self.dept_single_operation_api.format(self.organ.id, dept.id)
        )

        self.assert_response_success(resp)
        self.assertEquals(resp.get('code'), 10000)

        # 测试科室存在员工不能删除
        dept = self.create_department(self.organ, dept_name='存在员工科室')

        # 初始化staff相应数据
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        staff = self.create_completed_staff(self.organ, dept, name='测试员工', **staff_data)
        response = self.delete(
            self.dept_single_operation_api.format(self.organ.id, dept.id)
        )
        self.assert_response_failure(response)
        self.assertEquals(staff.dept.id, dept.id)
        self.assertEquals(response.get('code'), 0)

    def test_departments_list(self):
        """
        测试科室列表
        """
        self.login_with_username(self.user)
        dept = self.create_department(self.organ,
                                      dept_name='测试科室_{}'.format(self.get_random_suffix()))
        response = self.get(
            self.dept_list.format(self.organ.id)
        )

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('dept'))
        self.assert_object_in_results({'name': dept.name}, response.get('dept'))

    def test_hospital_global_data(self):
        """
        api测试: 返回医院全局数据
        :return:
        """
        API = "/api/v1/hospitals/{}/global-data"
        staff = self.create_completed_staff(self.organ, self.dept, name="普通员工")

        self.login_with_username(staff.user)
        response = self.get(API.format(self.organ.id))
        self.assert_response_success(response)
        self.assertIsNotNone(response.get("depts"))
        self.assertIsNotNone(response.get("flows"))
        self.assertIsNotNone(response.get("perm_groups"))

        staff.user.clear_cache()
        staff.clear_cache()

    def test_department_batch_upload(self):
        """
        测试批量导入部门
        :return:
        """
        api = '/api/v1/hospitals/{0}/departments/batch-upload'

        self.login_with_username(self.user)
        import os
        curr_path = os.path.dirname(__file__)
        dept_file_obj = open(curr_path+'/data/dept-normal-test.xlsx', 'rb')
        response = self.raw_post(api.format(self.organ.id), {'dept_excel_file': dept_file_obj})
        self.assert_response_success(response)


class StaffsPermChangeTestCase(BaseTestCase):
    """
    测试staff权限分配相关API
    """
    staffs_perm_change_api = '/api/v1/hospitals/{0}/staffs/change-permission'

    def test_staffs_perm_change(self):
        """
        测试管理员给员工非配权限
        """

        self.login_with_username(self.user)

        # 初始化staff相应数据
        staff_data = {
            'title': '主治医师',
            'contact': '19822012220',
            'email': 'ceshi01@test.com',
        }
        self.create_completed_staff(self.organ, self.dept, name='测试01', **staff_data)

        staffs = self.organ.get_staffs()
        groups = self.organ.get_all_groups()
        staff_id_list = [staff.id for staff in staffs]
        group_id_list = [g.id for g in groups]

        data = {
            'perm_group_id': random.sample(group_id_list, 1)[0],
            'staffs':        ','.join([str(id) for id in staff_id_list])
        }

        response = self.put(
            self.staffs_perm_change_api.format(self.organ.id),
            data=data
        )

        self.assert_response_success(response)
        self.assertEquals(response.get('msg'), '员工权限已修改')


class StaffAPITestCase(BaseTestCase):


    def test_staff_create(self):
        """
        测试新增员工信息
        :return:
        """
        api = '/api/v1/hospitals/{0}/staffs/create'

        self.login_with_username(self.user)

        new_staff_data = {
            'username': 'add_user_test001',
            'password': '123456',
            'staff_name': 'add_zhangsan_test001',
            'staff_title': 'zhuzhiyishi',
            'contact_phone': '13822012220',
            'email': 'zhangshang@test.com',
            'dept_id': self.dept.id,
            'group_id': '',
        }

        response = self.post(
            api.format(self.organ.id),
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
        api = '/api/v1/hospitals/{0}/staffs/{1}'

        self.login_with_username(self.user)
        # new_staff = self.create_completed_staff(self.organ, self.dept, 'test001')
        response = self.get(
            api.format(
                self.organ.id,
                self.admin_staff.id,
            )
        )
        self.assert_response_success(response)
        # self.assert_response_failure(response)
        self.assertIsNotNone(response.get('staff'), '没获取到员工信息')
        self.assertIsNotNone(response.get('staff').get('staff_name'), '没获取到员工姓名')
        self.assertEquals(response.get('staff').get('staff_name'), self.admin_staff.name)

    def test_staff_update(self):
        """
        测试更新员工信息
        :return:
        """
        api = '/api/v1/hospitals/{0}/staffs/{1}'

        self.login_with_username(self.user)

        update_staff_data = {
            'staff_name': 'add_zhangsan_test001',
            'staff_title': 'zhuzhiyishi',
            'contact_phone': '13822012220',
            'email': 'zhangshang@test.com',
            'dept_id': self.dept.id,
        }
        response = self.put(
            api.format(
                self.organ.id,
                self.admin_staff.id,
            ), data=update_staff_data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('staff'), '没获取到修改后的员工信息')
        self.assertIsNotNone(response.get('staff').get('staff_name'), '没有获取到修改后的员工姓名')
        self.assertEqual(response.get('staff').get('staff_name'), update_staff_data['staff_name'])

    def test_staff_delete(self):
        """
        测试删除员工信息
        :return:
        """
        api = '/api/v1/hospitals/{0}/staffs/{1}'

        self.login_with_username(self.user)
        response = self.delete(
            api.format(self.organ.id, self.admin_staff.id)
        )
        self.assert_response_failure(response)
        staff = self.create_completed_staff(organ=self.organ, dept=self.dept, name='test0001')
        response2 =  self.delete(
            api.format(self.organ.id, staff.id)
        )
        self.assert_response_success(response2)

    def test_staff_list(self):
        """
        测试获取员工列表
        :return:
        """
        api = '/api/v1/hospitals/{0}/staffs'
        self.create_completed_staff(self.organ, self.dept, 'test001')
        self.create_completed_staff(self.organ, self.dept, 'test002')
        self.login_with_username(self.user)
        response = self.get(
            api.format(self.organ.id),
            dept_id=self.dept.id,

        )
        self.assert_response_success(response)
        #self.assert_response_failure(response)
        self.assertIsNotNone(response.get('staffs'))
        self.assertEqual(len(response.get('staffs')), 3)

    def test_staff_batch_upload(self):
        """
        测试批量导入员工
        :return:
        """
        api = '/api/v1/hospitals/{0}/staffs/batch-upload'

        self.login_with_username(self.user)
        self.create_department(self.organ, dept_name='测试部门')
        import os
        curr_path = os.path.dirname(__file__)
        staff_file_obj = open(curr_path+'/data/staff-normal-test.xlsx', 'rb')
        response = self.raw_post(api.format(self.organ.id), {'staff_excel_file': staff_file_obj})
        self.assert_response_success(response)




