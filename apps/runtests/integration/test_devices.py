# coding=utf-8
#
# Created by zeng, on 2018/10/29
#

#

import logging

from nmis.devices.consts import ASSERT_DEVICE_STATUS_SCRAPPED
from runtests import BaseTestCase
from runtests.common.mixins import AssertDevicesMixin, HospitalMixin

from utils import times

logs = logging.getLogger(__name__)


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
        medical_devices_six8_cate = self.create_medical_device_cate(creator=self.user.get_profile())
        logs.info(medical_devices_six8_cate)

        self.assertIsNotNone(medical_devices_six8_cate)

        # 创建机构大楼信息
        title = '信息综合大楼'
        hospital_address = self.create_hospital_address(title=title)
        self.assertIsNotNone(hospital_address)
        self.assertEquals(hospital_address.title, title)
        # 创建大楼中的存储地点
        storage_place = self.create_storage_place(dept=self.dept, parent=hospital_address,
                                                  title='信息设备存储室_{}'.format(self.get_random_suffix()))
        self.assertIsNotNone(storage_place)
        self.assertIsNotNone(storage_place)
        medical_assert_device_data = {
            "assert_no": "TEST0007_{}".format(self.get_random_suffix()),
            "title": "柳叶刀",
            "medical_device_cate_id": medical_devices_six8_cate.id,
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
            self.assertEquals(value, medical_assert_device.get(key))
        # 创建信息化资产设备
        resp = self.post(api, data=information_assert_device_data)
        self.assert_response_success(resp)
        information_assert_device = resp.get('assert_device')
        self.assertIsNotNone(information_assert_device)
        for key, value in information_assert_device_data.items():
            self.assertEquals(value, information_assert_device.get(key))

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
        self.assertEquals(hospital_address.title, title)
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
        self.assertEquals(response.get('assert_device').get('id'), assert_device.id)

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
        self.assertEquals(hospital_address.title, title)
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
        self.assertEquals(update_assert_device.get('id'), assert_device.id)
        self.assertEquals(update_assert_device.get('status', '').strip(), ASSERT_DEVICE_STATUS_SCRAPPED)

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
        self.assertEquals(hospital_address.title, title)
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
        self.assertEquals(len(assert_device_list), 5)
        data = {
            'cate': 'IN',
            'search_key': '电脑',
            'status': 'US',
            'storage': str(storage_place.id),
            'page': 1,
            'size': 3
        }

        response = self.get(api, data=data)
        self.assert_response_success(response)
        assert_devices = response.get('assert_devices')
        self.assertIsNotNone(assert_devices)
        self.assertEquals(len(assert_devices), 3)
        for assert_device in assert_devices:
            self.assertEquals(assert_device.get('cate'), 'IN')
            self.assertEquals(assert_device.get('status'), 'US')
            self.assertEquals(assert_device.get('storage_place_id'), storage_place.id)

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
        self.assertEquals(hospital_address.title, title)
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
            'title': '电脑显示器'
        }
        response = self.put(api.format(assert_device.id), data=update_data)
        self.assert_response_success(response)
        update_assert_device = response.get('assert_device')
        self.assertIsNotNone(update_assert_device)
        self.assertEquals(update_assert_device.get('id'), assert_device.id)
        self.assertNotEquals(assert_device.title, update_assert_device.get('title'))
        self.assertEquals(update_assert_device.get('title'), update_data.get('title'))