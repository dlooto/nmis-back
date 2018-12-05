# coding=utf-8
#
# Created by junn, on 2018/6/11
#

import logging
import random
from unittest import skip

import pytest

from runtests import BaseTestCase
from runtests.common.mixins import HospitalMixin

logger = logging.getLogger('runtests')


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
        self.assertEqual(dept_data['name'], response.get('dept').get('name'))

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
        self.assertEqual(resp.get('code'), 10000)

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
        self.assertEqual(staff.dept.id, dept.id)
        self.assertEqual(response.get('code'), 0)

    def test_departments_list(self):
        """
        测试科室列表
        """
        api = '/api/v1/hospitals/{0}/departments'
        self.login_with_username(self.user)
        # 批量创建科室
        for index in range(0, 10):
            self.create_department(self.organ, dept_name='测试科室_{}'.format(self.get_random_suffix()))

        data = {
            'page': 1,
            'size': 4
        }
        response = self.get(
            api.format(self.organ.id), data=data
        )

        self.assert_response_success(response)
        self.assertIsNotNone(response.get('depts'))
        self.assertEqual(len(response.get('depts')), data.get('size'))

    def test_hospital_global_data(self):
        """
        api测试: 返回医院全局数据
        :return:
        """
        API = "/api/v1/hospitals/{}/global-data"
        staff = self.create_completed_staff(self.organ, self.dept, name="普通员工")

        self.login_with_username(self.user)
        response = self.get(API.format(self.organ.id))
        self.assert_response_success(response)
        self.assertIsNotNone(response.get("depts"))
        self.assertIsNotNone(response.get("flows"))
        self.assertIsNotNone(response.get("roles"))

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
        with open(curr_path+'/data/dept-normal-test.xlsx', 'rb') as file:
            response = self.raw_post(api.format(self.organ.id), {'dept_excel_file': file})
            self.assert_response_success(response)


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
        }

        response = self.post(
            api.format(self.organ.id),
            data=new_staff_data
        )
        self.assert_response_success(response)
        # self.assert_response_failure(response)  #暴露数据
        self.assertIsNotNone(response.get("staff"))
        self.assertIsNotNone(response.get("staff").get('staff_name'))
        self.assertEqual(response.get('staff').get('staff_name'), new_staff_data['staff_name'])

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
        self.assertEqual(response.get('staff').get('staff_name'), self.admin_staff.name)

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

        self.login_with_username(self.user)
        for index in range(0, 10):
            self.create_completed_staff(self.organ, self.dept, name='test_{}'.format(self.get_random_suffix()))

        data = {
            'page': 1,
            'size': 4
        }
        response = self.get(
            api.format(self.organ.id),
            dept_id=self.dept.id,
            data=data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('staffs'))
        self.assertEqual(len(response.get('staffs')), 4)

    def test_chunk_staff_list(self):
        """
        测试获取员工列表
        :return:
        """
        api = '/api/v1/hospitals/{0}/chunk_staffs'

        self.login_with_username(self.user)
        for index in range(0, 10):
            self.create_completed_staff(self.organ, self.dept, name='test_{}'.format(self.get_random_suffix()))

        data = {
            'page': 1,
            'size': 4
        }
        response = self.get(
            api.format(self.organ.id),
            dept_id=self.dept.id,
            data=data
        )
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('staffs'))
        self.assertEqual(len(response.get('staffs')), 4)

    def test_staff_batch_upload(self):
        """
        测试批量导入员工
        :return:
        """
        import os

        api = '/api/v1/hospitals/{0}/staffs/batch-upload'

        self.login_with_username(self.user)

        curr_path = os.path.dirname(__file__)
        with open(curr_path+'/data/staff-normal-test.xlsx', 'rb') as file:
            response = self.raw_post(api.format(self.organ.id), {'staff_excel_file': file})
            self.assert_response_form_errors(response)

            self.create_department(self.organ, dept_name='信息科')
            self.create_department(self.organ, dept_name='测试部门')
        with open(curr_path + '/data/staff-normal-test.xlsx', 'rb') as file:
            response = self.raw_post(api.format(self.organ.id), {'staff_excel_file': file})
            self.assert_response_success(response)


class RoleAPITestCase(BaseTestCase):

    def test_add_roles(self):
        """
        测试添加角色
        :return:
        """
        api = '/api/v1/hospitals/roles/create'
        self.login_with_username(self.user)
        from nmis.hospitals.models import Role
        from django.contrib.auth.models import Permission

        role = Role.objects.get_super_admin().first()
        role_data = {
            'name': '测试角色001',
            'codename': 'ceshi001',
            'desc': '描述',
            'permissions': [
                Permission.objects.filter(
                    content_type__app_label='hospitals',
                    content_type__model='hospital'
                ).first().id,
            ]
        }
        response = self.post(api.format(), data=role_data)
        self.assert_response_success(response)
        role = response.get('role')
        self.assertEqual(role.get('name'), role_data.get('name'))
        self.assertEqual(role.get('desc'), role_data.get('desc'))
        self.assertEqual(role.get('permissions')[0].get('id'), role_data.get('permissions')[0])

    # def test_view_role(self):
    #     api = '/api/v1/hospitals/roles/{0}'

    def test_role_list(self):
        api = '/api/v1/hospitals/roles'
        self.login_with_username(self.user)
        from django.contrib.auth.models import Permission
        from nmis.hospitals.models import Role

        permissions = Permission.objects.filter(content_type__app_label='hospitals', content_type__model='hospital')

        init_roles = Role.objects.all()
        init_roles_len = len(init_roles)
        data1 = {'name': '测试角色0001', 'codename': 'ceshi0001', 'permissions': [permissions[0]]}
        data2 = {'name': '测试角色0002', 'codename': 'ceshi0002', 'permissions': [permissions[1]]}
        role1 = Role.objects.create_role_with_permissions(data=data1)
        role2 = Role.objects.create_role_with_permissions(data=data2)
        resp1 = self.get(api.format())
        self.assert_response_success(resp1)
        roles = resp1['roles']
        self.assertIsNotNone(roles)
        # 测试数据库和本地数据库串号，导致匹配结果有误
        self.assertEqual(2, len(roles)-init_roles_len)
        role_names = []
        for role in roles:
            role_names.append(role['name'])

        self.assertTrue((data1['name'] in role_names or data2['name'] in role_names))


class HospitalAddressApiTestCase(BaseTestCase, HospitalMixin):

    def test_get_storage_places(self):
        """测试获取存储地址列表"""
        api = '/api/v1/hospitals/{}/storage-places'

        self.login_with_username(self.user)
        init_addresses = self.init_hospital_address(self.dept)
        self.assertIsNotNone(init_addresses)
        self.assertTrue(len(init_addresses) > 2)
        storage_places = [item for item in init_addresses if item.is_storage_place]
        self.assertIsNotNone(storage_places)
        self.assertTrue(len(storage_places) > 2)
        response = self.get(api.format(self.organ.id))
        self.assert_response_success(response)
        addresses = response.get('hospital_addresses')
        self.assertIsNotNone(addresses)
        self.assertEqual(len(addresses), len(storage_places))

    def test_get_hospital_address_tree(self):
        """测试获取医院内部地址树形结构"""
        api = '/api/v1/hospitals/{}/hospital-address-tree'

        self.login_with_username(self.user)
        init_addresses = self.init_hospital_address(self.dept)
        self.assertIsNotNone(init_addresses)
        self.assertTrue(len(init_addresses) > 2)
        root_addresses = [item for item in init_addresses if not item.parent]
        self.assertTrue(len(root_addresses) == 1)
        root_address = root_addresses[0]
        storage_places = [item for item in init_addresses if item.is_storage_place]
        self.assertTrue(len(storage_places) > 0)
        response = self.get(api.format(self.organ.id))
        self.assert_response_success(response)
        address_tree = response.get('hospital_addresses')
        self.assertIsNotNone(address_tree)
        self.assertEqual(address_tree.get('id'), root_address.id)
        self.assertIsNotNone(address_tree.get('children'))

    def test_create_hospital_address(self):
        """测试创建医院内部地址"""
        api = '/api/v1/hospitals/{}/hospital-addresses/create'

        self.login_with_username(self.user)
        root_address_data = {
            'title': 'XX医院',
            'is_storage_place': False,
            'parent_id': None,
            'desc': ''
        }
        resp_root = self.post(api.format(self.organ.id), data=root_address_data)
        self.assert_response_success(resp_root)
        root_address = resp_root.get('hosp_address')
        self.assertIsNotNone(root_address)
        self.assertIsNotNone(root_address.get('id'))
        self.assertEqual(root_address.get('title'), root_address_data.get('title'))
        self.assertEqual(root_address.get('is_storage_place'), root_address_data.get('is_storage_place'))
        self.assertEqual(root_address.get('parent_id'), root_address_data.get('parent_id'))
        self.assertEqual(root_address.get('desc'), root_address_data.get('desc'))

        storage_place_data = {
            'title': 'A仓库',
            'is_storage_place': True,
            'parent_id': root_address.get('id'),
            'desc': ''
        }
        resp_sp = self.post(api.format(self.organ.id), data=storage_place_data)
        self.assert_response_success(resp_sp)
        storage_place = resp_sp.get('hosp_address')
        self.assertIsNotNone(storage_place)
        self.assertIsNotNone(storage_place.get('id'))
        self.assertEqual(storage_place.get('title'), storage_place_data.get('title'))
        self.assertEqual(storage_place.get('is_storage_place'), storage_place_data.get('is_storage_place'))
        self.assertEqual(storage_place.get('parent_id'), storage_place_data.get('parent_id'))
        self.assertEqual(storage_place.get('desc'), storage_place_data.get('desc'))







