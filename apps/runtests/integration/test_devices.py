# coding=utf-8
#
# Created by zeng, on 2018/10/29
#

#

import logging

from django.core.files.uploadedfile import UploadedFile

import settings
from nmis.devices.consts import ASSERT_DEVICE_STATUS_SCRAPPED
from nmis.documents.consts import DOC_UPLOAD_BASE_DIR
from runtests import BaseTestCase
from runtests.common.mixins import AssertDevicesMixin, HospitalMixin
from utils.files import remove, upload_file
from utils.times import now

logger = logging.getLogger(__name__)


class AssertDevicesApiTestCase(BaseTestCase, AssertDevicesMixin, HospitalMixin):

    def test_create_assert_device(self):
        """
        API测试：新建资产设备（医疗设备/信息化设备）
        """
        api = '/api/v1/devices/create'

        self.login_with_username(self.user)
        # 创建负责人
        performer_data = {
            'title': '设备负责人',
            'contact': '18943823433',
            'email': 'nmis@qq.com'
        }
        performer = self.create_completed_staff(self.organ, self.dept, name='张三', **performer_data)
        # 创建使用部门
        use_department = self.create_department(self.organ, dept_name='测试科室')
        # 创建医疗器械68分类数据
        medical_devices_cate = self.create_medical_device_cate(creator=self.user.get_profile())
        self.assertIsNotNone(medical_devices_cate)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address,
                                                  title='信息设备存储室_{}'.format(self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        self.assertIsNotNone(storage_place)
        medical_assert_device_data = {
            "assert_no": "TEST0007_{}".format(self.get_random_suffix()),
            "title": "柳叶刀",
            "medical_device_cate_id": medical_devices_cate.id,
            "serial_no": "TEST03420352_{}".format(self.get_random_suffix()),
            "type_spec": "BN3004",
            "service_life": 3,
            "performer_id": performer.id,
            "responsible_dept_id": self.dept.id,
            "use_dept_id": use_department.id,
            "production_date": "2018-09-12",
            "bar_code": "123123123_{}".format(self.get_random_suffix()),
            "status": "US",
            "storage_place_id": storage_place.id,
            "purchase_date": "2018-10-09",
            "cate": "ME",
        }

        information_assert_device_data = {
            "assert_no": "TEST0008_{}".format(self.get_random_suffix()),
            "title": "Mac电脑",
            "serial_no": "TEST03420353_{}".format(self.get_random_suffix()),
            "type_spec": "BN3004",
            "service_life": 3,
            "performer_id": performer.id,
            "responsible_dept_id": self.dept.id,
            "use_dept_id": use_department.id,
            "production_date": "2018-09-12",
            "bar_code": "123123124_{}".format(self.get_random_suffix()),
            "status": "US",
            "storage_place_id": storage_place.id,
            "purchase_date": "2018-10-09",
            "cate": "IN"
        }
        # 创建医疗设备资产
        response = self.post(api, data=medical_assert_device_data)
        self.assert_response_success(response)
        medical_assert_device = response.get('assert_device')
        self.assertIsNotNone(medical_assert_device)
        for key, value in medical_assert_device_data.items():
            self.assertEqual(value, medical_assert_device.get(key))
        # 创建信息化资产设备
        resp = self.post(api, data=information_assert_device_data)
        self.assert_response_success(resp)
        information_assert_device = resp.get('assert_device')
        self.assertIsNotNone(information_assert_device)
        for key, value in information_assert_device_data.items():
            self.assertEqual(value, information_assert_device.get(key))

    def test_assert_device_detail(self):
        """
        API测试: 查看资产设备详情
        """
        api = '/api/v1/devices/{}'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address, title='信息设备存储室_{}'.format(self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        # 创建信息化资产设备
        assert_device = self.create_assert_device(
            title="电脑_{}".format(self.get_random_suffix()),
            dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
            assert_no="TEST0008_{}".format(self.get_random_suffix()),
            bar_code="123123124_{}".format(self.get_random_suffix()),
            serial_no="TEST03420353_{}".format(self.get_random_suffix()),
        )

        response = self.get(api.format(assert_device.id))
        self.assert_response_success(response)
        self.assertIsNotNone(response.get('assert_device'))
        self.assertEqual(response.get('assert_device').get('id'), assert_device.id)

    def test_assert_device_scrap(self):
        """
        API测试: 对设备进行报废操作API接口测试
        """
        api = '/api/v1/devices/{}/scrap'
        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address,
                                                  title='信息设备存储室_{}'.format(
                                                      self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        # 创建信息化资产设备
        assert_device = self.create_assert_device(
            title="电脑_{}".format(self.get_random_suffix()),
            dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
            assert_no="TEST0008_{}".format(self.get_random_suffix()),
            bar_code="123123124_{}".format(self.get_random_suffix()),
            serial_no="TEST03420353_{}".format(self.get_random_suffix()),
        )

        response = self.put(api.format(assert_device.id))
        self.assert_response_success(response)
        update_assert_device = response.get('assert_device')
        self.assertIsNotNone(update_assert_device)
        self.assertEqual(update_assert_device.get('id'), assert_device.id)
        self.assertEqual(update_assert_device.get('status', '').strip(), ASSERT_DEVICE_STATUS_SCRAPPED)

    def test_assert_devices(self):
        """
        API测试: 资产设备列表API接口测试
        """
        api = '/api/v1/devices/assert-devices'

        self.login_with_username(self.user)
        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(
            dept=self.dept, parent=hospital_address, title='信息设备存储室_{}'.format(self.get_random_suffix())
        )
        assert_device_list = []
        for i in range(5):
            assert_device_list.append(
                self.create_assert_device(
                    title="电脑_{}".format(self.get_random_suffix()),
                    dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
                    assert_no="TEST0008_{}".format(self.get_random_suffix()),
                    bar_code="123123124_{}".format(self.get_random_suffix()),
                    serial_no="TEST03420353_{}".format(self.get_random_suffix()),
                )
            )
        self.assertIsNotNone(assert_device_list)
        self.assertEqual(len(assert_device_list), 5)
        data = {
            'cate': 'IN',
            'search_key': '电脑',
            'status': 'US',
            'storage': str(storage_place.id),
            'page': 1,
            'size': 3,
            'type': 'TL'
        }
        response = self.get(api, data=data)
        self.assert_response_success(response)
        assert_devices = response.get('assert_devices')
        self.assertIsNotNone(assert_devices)
        self.assertEqual(len(assert_devices), 3)
        for assert_device in assert_devices:
            self.assertEqual(assert_device.get('cate'), 'IN')
            self.assertEqual(assert_device.get('status'), 'US')
            self.assertEqual(assert_device.get('storage_place_id'), storage_place.id)

    def test_update_assert_device(self):
        """
        API测试: 修改资产设备API接口测试
        """
        api = '/api/v1/devices/{}'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address,
                                                  title='信息设备存储室_{}'.format(
                                                      self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        # 创建信息化资产设备
        assert_device = self.create_assert_device(
            title="电脑_{}".format(self.get_random_suffix()),
            dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
            assert_no="TEST0008_{}".format(self.get_random_suffix()),
            bar_code="123123124_{}".format(self.get_random_suffix()),
            serial_no="TEST03420353_{}".format(self.get_random_suffix()),
        )
        update_data = {
            'title': '电脑显示器',
            'assert_no': 'ABSDEFG',
            'serial_no': 'ASQ123123',
            'type_spec': 'TYPE123',
            'service_life': 12,
            'production_date': '2018-06-01',
            'status': 'US',
            'storage_place_id': storage_place.id,
            'purchase_date': '2018-06-08'

        }
        response = self.put(api.format(assert_device.id), data=update_data)
        self.assert_response_success(response)
        update_assert_device = response.get('assert_device')
        self.assertIsNotNone(update_assert_device)
        self.assertEqual(update_assert_device.get('id'), assert_device.id)
        self.assertNotEqual(assert_device.title, update_assert_device.get('title'))
        self.assertEqual(update_assert_device.get('title'), update_data.get('title'))

    def test_delete_assert_device(self):
        """
        API测试: 删除资产设备API接口测试
        """
        api = '/api/v1/devices/{}'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address,
                                                  title='信息设备存储室_{}'.format(
                                                      self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        # 创建信息化资产设备
        assert_device = self.create_assert_device(
            title="电脑_{}".format(self.get_random_suffix()),
            dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
            assert_no="TEST0008_{}".format(self.get_random_suffix()),
            bar_code="123123124_{}".format(self.get_random_suffix()),
            serial_no="TEST03420353_{}".format(self.get_random_suffix()),
        )

        response = self.delete(api.format(assert_device.id))
        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)

        device = self.get_assert_device(assert_device.id)
        self.assertIsNone(device)

    def test_allocate_assert_device(self):
        """
        API测试: 资产设备调配操作（单个调配/批量调配）
        """
        api = '/api/v1/devices/allocate'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(
            dept=self.dept, parent=hospital_address, title='信息设备存储室_{}'.format(self.get_random_suffix())
        )
        assert_devices = []
        for i in range(5):
            assert_devices.append(
                self.create_assert_device(
                    title="打印机_{}".format(self.get_random_suffix()),
                    dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
                    assert_no="TEST0008_{}".format(self.get_random_suffix()),
                    bar_code="123123124_{}".format(self.get_random_suffix()),
                    serial_no="TEST03420353_{}".format(self.get_random_suffix()),
                )
            )
        self.assertIsNotNone(assert_devices)
        self.assertEqual(len(assert_devices), 5)
        # 创建使用科室
        department = self.create_department(self.organ, dept_name='很吊的科室_{}'.format(self.get_random_suffix()))

        assert_device_ids = ",".join([str(devices.id) for devices in assert_devices])
        data = {
            "use_dept_id": department.id,
            "assert_device_ids": assert_device_ids
        }
        response = self.put(api, data=data)
        self.assert_response_success(response)
        assert_device_list = response.get('assert_devices')
        self.assertIsNotNone(assert_device_list)
        self.assertEqual(len(assert_device_list), 5)

        for assert_device in assert_device_list:
            self.assertIsNotNone(assert_device.get('use_dept_id'))
            self.assertEqual(assert_device.get('use_dept_id'), department.id)

    def test_assert_device_batch_upload(self):
        """
        API测试: 资产设备批量导入API接口测试
        """
        api = '/api/v1/devices/assert_devices/batch-upload'

        self.login_with_username(self.user)
        # 创建测试科室
        dept = self.create_department(self.organ, dept_name='测试科室')
        # 创建负责人
        performer_data = {
            'title': '设备负责人',
            'contact': '18943823433',
            'email': 'nmis@qq.com'
        }
        performer = self.create_completed_staff(self.organ, self.dept, name='曾老师', **performer_data)
        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(
            dept=self.dept, parent=hospital_address,
            title='信息设备存储室'
        )
        self.assertIsNotNone(storage_place)
        self.assertEqual(storage_place.parent.id, hospital_address.id)
        # 创建医疗器械68分类数据
        medical_devices_cate = self.create_medical_device_cate(
            creator=self.user.get_profile())
        self.assertIsNotNone(medical_devices_cate)

        import os
        curr_path = os.path.dirname(__file__)
        with open(curr_path + '/data/medical_assert_devices.xlsx', 'rb') as file_obj:
            response = self.raw_post(
                api, {
                    'file': file_obj,
                    'cate': 'ME'
                })
        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)


class MaintenancePlanTestCase(BaseTestCase, AssertDevicesMixin, HospitalMixin):

    def test_create_maintenance_plan(self):
        """
        API测试: 新建设备维护API接口测试
        """
        api = '/api/v1/devices/maintenance_plan/create'

        self.login_with_username(self.user)
        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(
            dept=self.dept, parent=hospital_address,
            title='信息设备存储室_{}'.format(self.get_random_suffix())
        )
        self.assertIsNotNone(storage_place)
        self.assertEqual(hospital_address.id, storage_place.parent.id)
        assert_devices = []
        for i in range(5):
            assert_devices.append(
                self.create_assert_device(
                    title="复印机_{}".format(self.get_random_suffix()),
                    dept=self.dept, storage_place=storage_place, creator=self.admin_staff,
                    assert_no="TEST0008_{}".format(self.get_random_suffix()),
                    bar_code="123123124_{}".format(self.get_random_suffix()),
                    serial_no="TEST03420353_{}".format(self.get_random_suffix()),
                )
            )
        data = {
          "title": "普通设备维护",
          "storage_place_ids": str(storage_place.id),
          "type": "PL",
          "start_date": now().strftime('%Y-%m-%d'),
          "expired_date": now().strftime('%Y-%m-%d'),
          "executor_id": self.admin_staff.id,
          "assert_device_ids": ",".join([str(assert_device.id) for assert_device in assert_devices])
        }
        response = self.post(api, data=data)
        self.assert_response_success(response)
        maintenance_plan = response.get('maintenance_plan')
        self.assertIsNotNone(maintenance_plan)
        self.assertEqual(maintenance_plan.get('title'), data.get('title'))
        self.assertEqual(maintenance_plan.get('status'), 'NW')
        self.assertEqual(
            len(maintenance_plan.get('assert_devices')),
            len(data.get('assert_device_ids').strip(',').split(','))
        )

    def test_maintenance_plans(self):
        """
        API测试: 资产设备维护列表API接口测试
        """
        api = '/api/v1/devices/maintenance_plans'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_places = []
        for i in range(2):
            storage_places.append(
                self.create_storage_place(
                    dept=self.dept, parent=hospital_address,
                    title='信息设备存储室_{}'.format(self.get_random_suffix())
                )
            )
        self.assertIsNotNone(storage_places)
        self.assertEqual(len(storage_places), 2)

        assert_devices = []
        for storage_place in storage_places:
            for i in range(3):
                assert_devices.append(
                    self.create_assert_device(
                        title="测试信息化资产设备_{}".format(self.get_random_suffix()),
                        dept=self.dept, storage_place=storage_place,
                        creator=self.admin_staff,
                        assert_no="TEST0008_{}".format(self.get_random_suffix()),
                        bar_code="123123124_{}".format(self.get_random_suffix()),
                        serial_no="TEST03420353_{}".format(self.get_random_suffix()),
                    )
                )
        self.assertIsNotNone(assert_devices)
        self.assertEqual(len(assert_devices), 6)
        maintenance_plans = []
        for j in range(5):
            maintenance_plans.append(
                self.create_maintenance_plan(
                    title="资产设备维护计划_{}".format(self.get_random_suffix()),
                    storage_places=storage_places, executor=self.admin_staff,
                    creator=self.admin_staff,
                    assert_devices=assert_devices
                )
            )
        self.assertIsNotNone(maintenance_plans)
        self.assertEqual(len(maintenance_plans), 5)
        query_data = {
            'search_key': '维护',
            'period': 'OM',
            'status': 'NW',
            'page': '1',
            'size': '3'
        }
        response = self.get(api, data=query_data)
        self.assert_response_success(response)
        maintenance_plan_list = response.get('maintenance_plans')
        self.assertIsNotNone(maintenance_plan_list)
        self.assertEqual(len(maintenance_plan_list), 3)
        for maintenance_plan in maintenance_plan_list:
            self.assertEqual(maintenance_plan.get('status'), 'NW')

    def test_maintenance_plan_detail(self):
        """
        API测试: 资产设备维护计划详情
        """
        api = '/api/v1/devices/maintenance_plan/{}'

        self.login_with_username(self.user)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEqual(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(
                    dept=self.dept, parent=hospital_address,
                    title='信息设备存储室_{}'.format(self.get_random_suffix())
                )
        self.assertIsNotNone(storage_place)
        self.assertEqual(storage_place.parent.id, hospital_address.id)
        assert_devices = []
        for i in range(3):
            assert_devices.append(
                self.create_assert_device(
                    title="测试信息化资产设备_{}".format(self.get_random_suffix()),
                    dept=self.dept, storage_place=storage_place,
                    creator=self.admin_staff,
                    assert_no="TEST0008_{}".format(self.get_random_suffix()),
                    bar_code="123123124_{}".format(self.get_random_suffix()),
                    serial_no="TEST03420353_{}".format(self.get_random_suffix()),
                )
            )
        self.assertIsNotNone(assert_devices)
        self.assertEqual(len(assert_devices), 3)

        maintenance_plan = self.create_maintenance_plan(
                    title="资产设备维护计划_{}".format(self.get_random_suffix()),
                    storage_places=[storage_place], executor=self.admin_staff,
                    creator=self.admin_staff,
                    assert_devices=assert_devices
                )
        self.assertIsNotNone(maintenance_plan)

        response = self.get(api.format(maintenance_plan.id))
        self.assert_response_success(response)
        m_plan = response.get('maintenance_plan')
        self.assertIsNotNone(m_plan)
        self.assertEqual(m_plan.get('id'), maintenance_plan.id)


class RepairOrderTestCase(BaseTestCase, AssertDevicesMixin, HospitalMixin):

    def test_fault_type_list(self):
        """测试获取故障类型列表"""
        api = '/api/v1/devices/fault_types'

        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)
        response = self.get(api.format())
        self.assert_response_success(response)
        fault_types_get = response.get('fault_types')
        self.assertTrue(len(fault_types_get) == len(fault_types))

    def test_repair_order_create_or_get(self):
        """
        测试提交报修单/获取单个报修单
        :return:
        """
        api_post = '/api/v1/devices/repair_orders/create'
        api_get = '/api/v1/devices/repair_orders/{}'

        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)

        new_data = {
            'applicant_id': self.admin_staff.id,
            'fault_type_id': fault_types[0].id,
            'desc': '电脑蓝屏desc'
        }
        response = self.post(api_post.format(), data=new_data)
        self.assert_response_success(response)
        repair_order = response.get('repair_order')
        self.assertIsNotNone(repair_order)
        self.assertIsNotNone(repair_order.get('order_no'))
        self.assertIsNotNone(repair_order.get('id'))
        response = self.get(api_get.format(repair_order.get('id')))
        self.assert_response_success(response)
        repair_order_get = response.get('repair_order')
        self.assertEqual(repair_order, repair_order_get)

    def test_dispatch_repair_order(self):
        api_get_list = '/api/v1/devices/repair_orders?page={}&size={}&action={}'
        api_put = '/api/v1/devices/repair_orders/{}'
        api_upload = '/api/v1/documents/upload-file'

        self.login_with_username(self.user)
        orders = self.init_repair_orders(self.admin_staff, self.admin_staff)
        # 获取我提交的报修单
        response = self.get(api_get_list.format(1, 10, 'MRO'), )
        self.assert_response_success(response)
        self.assertTrue(len(response.get('repair_orders')) == 2)

        # 获取待我分派的报修单
        response = self.get(api_get_list.format(1, 10, 'TDO'), )
        self.assert_response_success(response)
        repair_orders = response.get('repair_orders')
        self.assertTrue(len(repair_orders) == 2)
        # 测试分派
        order = repair_orders[0]
        dispatch_data = {
            'action': 'DSP',
            'maintainer_id': self.admin_staff.id,
            'priority': 'H'
        }
        response = self.put(api_put.format(order.get('id')), data=dispatch_data)
        self.assert_response_success(response)
        self.assertEqual(dispatch_data.get('priority'), response.get('repair_order').get('priority'))
        self.assertIsNotNone(response.get('repair_order').get('maintainer_id'))
        self.assertEqual(response.get('repair_order').get('status'), 'DNG')

        # 获取我维修的报修单

        response = self.get(api_get_list.format(1, 10, 'MMO'), )
        self.assert_response_success(response)
        repair_orders = response.get('repair_orders')
        self.assertTrue(len(repair_orders) == 1)
        import os
        curr_path = os.path.dirname(__file__)

        with open(curr_path+'/data/upload_file_test.xlsx', 'rb') as file_obj:
            response = self.raw_post(api_upload, {'file': file_obj})
            self.assert_response_success(response)
            files = response.get('file')
            try:
                self.assertIsNotNone(files)
                self.assertIsNotNone(files[0])
                self.assertIsNotNone(files[0].get('name'))
                self.assertIsNotNone(files[0].get('path'))
            # 测试处理报修单
                handle_data = {
                    'action': 'HDL',
                    'result': "已处理",
                    'expenses': 1,
                    # 'files': [
                    #     {
                    #         'name': files[0].get('name'),
                    #         'path': files[0].get('path'),
                    #         'cate': 'UNKNOWN'
                    #     }
                    # ]
                }
                response = self.put(api_put.format(order.get('id')), data=handle_data)
                self.assert_response_success(response)
                self.assertEqual(response.get('repair_order').get('status'), 'DNE')
                self.assertEqual(response.get('repair_order').get('result'), handle_data.get('result'))
                self.assertEqual(response.get('repair_order').get('expenses'), handle_data.get('expenses'))
            finally:
                remove(os.path.join(settings.MEDIA_ROOT, files[0].get('path')))


        # 测试评价
        comment_data = {
            'action': 'CMT',
            'comment_grade': 1,
            'comment_content': '工程师很棒'

        }
        response = self.put(api_put.format(order.get('id')), data=comment_data)
        self.assert_response_success(response)
        self.assertEqual(response.get('repair_order').get('status'), 'CLS')
        self.assertEqual(response.get('repair_order').get('comment_grade'), comment_data.get('comment_grade'))
        self.assertEqual(response.get('repair_order').get('comment_content'), comment_data.get('comment_content'))


class FaultSolutionsTestCase(BaseTestCase, AssertDevicesMixin, HospitalMixin):

    def test_create_fault_solution(self):

        api_create = '/api/v1/devices/fault_solutions/create'

        import os
        curr_path = os.path.dirname(__file__)
        fault_types = self.init_fault_types(self.admin_staff)
        self.login_with_username(self.user)

        with open(curr_path + '/data/upload_file_test.xlsx', 'wb+') as file_io:
            try:
                upload_result = upload_file(UploadedFile(file_io), DOC_UPLOAD_BASE_DIR)
                file_name = upload_result.get('name')
                file_path = upload_result.get('path')
                file = {'name': file_name, 'path': file_path, 'cate': "UNKNOWN"}
                fs_data = {
                    "title": "电脑碎屏001",
                    "fault_type_id": fault_types[0].id,
                    "desc": "电脑碎屏test",
                    "solution": "换机",
                    'files': [file]
                }
                response = self.post(api_create, data=fs_data)
                self.assert_response_success(response)
                fault_solution = response.get('fault_solution')
                self.assertIsNotNone(fault_solution)
                self.assertIsNotNone(fault_solution.get('id'))
                self.assertEqual(fault_solution.get('title'), fs_data.get('title'))
                self.assertEqual(fault_solution.get('fault_type_id'),
                                 fs_data.get('fault_type_id'))
                self.assertEqual(fault_solution.get('desc'), fs_data.get('desc'))
                self.assertEqual(fault_solution.get('solution'), fs_data.get('solution'))
            finally:
                remove(os.path.join(settings.MEDIA_ROOT, file_path))

    def test_update_fault_solution(self):

        api_update = '/api/v1/devices/fault_solutions/{}'

        fault_types = self.init_fault_types(self.admin_staff)
        fs_create_data = {
            "title": "电脑碎屏001",
            "fault_type": fault_types[2],
            "desc": "电脑碎屏test",
            "solution": "换机",
            'creator': self.admin_staff
        }
        fault_solution_create = self.create_fault_solution(
            fs_create_data.get('title'),
            fs_create_data.get('fault_type'),
            fs_create_data.get('desc'),
            fs_create_data.get('solution'),
            fs_create_data.get('creator')
        )
        fs_update_data = {
            "title": "电脑碎屏002",
            "fault_type_id": fault_types[0].id,
            "desc": "电脑碎屏test002",
            "solution": "换机002"
        }
        self.login_with_username(self.user)

        response = self.put(api_update.format(fault_solution_create.id), data=fs_update_data)
        self.assert_response_success(response)
        fault_solution = response.get('fault_solution')
        self.assertIsNotNone(fault_solution)
        self.assertIsNotNone(fault_solution.get('id'))
        self.assertEqual(fault_solution.get('title'), fs_update_data.get('title'))
        self.assertEqual(fault_solution.get('fault_type'), fs_update_data.get('fault_type'))
        self.assertEqual(fault_solution.get('desc'), fs_update_data.get('desc'))
        self.assertEqual(fault_solution.get('solution'), fs_update_data.get('solution'))

    def test_fault_solution_list(self):

        api = '/api/v1/devices/fault_solutions'
        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)
        self.create_fault_solution(
            '电脑碎屏002', fault_types[0], '电脑碎屏desc', '换机', self.admin_staff
        )
        response = self.get(api.format())
        self.assert_response_success(response)
        fault_solutions = response.get('fault_solutions')
        self.assertIsNotNone(fault_solutions)
        self.assertTrue(len(fault_solutions) == 1)

    def test_fault_solution_info(self):

        api = '/api/v1/devices/fault_solutions/{}'
        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)
        fs = self.create_fault_solution(
            '电脑碎屏002', fault_types[0], '电脑碎屏desc', '换机', self.admin_staff
        )
        response = self.get(api.format(fs.id))
        self.assert_response_success(response)
        fault_solution = response.get('fault_solution')
        self.assertIsNotNone(fault_solution)
        self.assertEqual(fault_solution.get('id'), fs.id)
        self.assertEqual(fault_solution.get('title'), fs.title)
        self.assertEqual(fault_solution.get('fault_type_id'), fs.fault_type_id)
        self.assertEqual(fault_solution.get('desc'), fs.desc)
        self.assertEqual(fault_solution.get('solution'), fs.solution)

    def test_delete_fault_solution(self):
        api = '/api/v1/devices/fault_solutions/batch-delete'
        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)
        fs = self.create_fault_solution(
            '电脑碎屏002', fault_types[0], '电脑碎屏desc', '换机', self.admin_staff
        )
        fs2 = self.create_fault_solution(
            '电脑碎屏003', fault_types[0], '电脑碎屏desc2', '换机3', self.admin_staff
        )
        ids = [fs.id, fs2.id]
        response = self.post(api, data={'ids': ids})
        self.assert_response_success(response)
        self.assertEqual(response.get('code'), 10000)

    def test_import_fault_solution(self):

        api = '/api/v1/devices/fault_solutions/import'
        self.login_with_username(self.user)
        fault_types = self.init_fault_types(self.admin_staff)

        import os
        curr_path = os.path.dirname(__file__)
        with open(curr_path + '/data/upload_fault_solution_test.xlsx', 'rb') as file:
            response = self.raw_post(api, {'file': file})
        self.assert_response_success(response)


class MedicalDeviceCateTestCase(BaseTestCase, AssertDevicesMixin, HospitalMixin):

    def test_get_med_dev_cate_catalog(self):
        """测试获取医疗器械分类目录"""

        api = '/api/v1/devices/medical-device-cate-catalogs'

        init_cates = self.init_medical_device_cates(self.admin_staff)
        init_catalogs = [cate for cate in init_cates if not cate.parent]
        self.assertIsNotNone(init_catalogs)
        self.login_with_username(self.user)
        resp = self.get(api)
        self.assert_response_success(resp)
        catalogs = resp.get('cate_catalogs')
        self.assertIsNotNone(catalogs)
        self.assertEqual(len(catalogs), len(init_catalogs))

    def test_get_all_med_dev_cates(self):
        """测试获取所有医疗器械二级分类"""
        api = '/api/v1/devices/medical-device-cates'

        init_cates = self.init_medical_device_cates(self.admin_staff)
        init_second_cates = [cate for cate in init_cates if cate.level==2]
        self.assertIsNotNone(init_second_cates)
        self.login_with_username(self.user)
        resp = self.get(api)
        self.assert_response_success(resp)
        medical_device_cates = resp.get('medical_device_cates')
        self.assertIsNotNone(medical_device_cates)
        self.assertEqual(len(init_second_cates), len(medical_device_cates))

    def test_get_med_dev_cates_by_catalog(self):
        """测试根据目录ID获取医疗器械二级分类"""

        api = '/api/v1/devices/medical-device-cate-catalogs/{}/medical-device-cates'

        init_cates = self.init_medical_device_cates(self.admin_staff)
        init_catalogs = [cate for cate in init_cates if not cate.parent]
        self.assertIsNotNone(init_catalogs)
        init_catalog_second_cates = [
            cate for cate in init_cates
            if cate.parent and cate.parent.parent and cate.parent.parent == init_catalogs[0]
        ]
        self.assertIsNotNone(init_catalog_second_cates)
        self.login_with_username(self.user)
        resp = self.get(api.format(init_catalogs[0]))
        self.assert_response_success(resp)
        medical_device_cates = resp.get('medical_device_cates')
        self.assertIsNotNone(medical_device_cates)
        self.assertEqual(len(init_catalog_second_cates), len(medical_device_cates))

    def test_upload_med_dev_cates(self):
        """测试上传医疗器械分类"""

        api = '/api/v1/devices/medical-device-cates/import'
        api_get_catlogs = '/api/v1/devices/medical-device-cate-catalogs'
        api_get_cates = '/api/v1/devices/medical-device-cates'

        self.login_with_username(self.user)
        import os
        curr_path = os.path.dirname(__file__)
        with open(curr_path+'/data/med_dev_cate_test.xlsx', 'rb') as file:
            response = self.raw_post(api.format(self.organ.id), {'file': file})
            self.assert_response_success(response)
        response = self.get(api_get_catlogs)
        self.assert_response_success(response)
        catalogs = response.get('cate_catalogs')
        self.assertIsNotNone(catalogs)

        response = self.get(api_get_cates)
        self.assert_response_success(response)
        medical_device_cates = response.get('medical_device_cates')
        self.assertIsNotNone(medical_device_cates)







