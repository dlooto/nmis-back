# coding=utf-8
#
# Created by zeng, on 2018/10/29
#

#

import logging

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
        medical_devices_six8_cate = self.create_medical_devices_six8_cate(creator=self.user.get_profile())
        self.assertIsNotNone(medical_devices_six8_cate)

        # 创建资产设备存储地点
        storage_places = self.create_storage_places(dept=self.dept)
        self.assertIsNotNone(storage_places)
        medical_assert_device_data = {
            "assert_no": "TEST0007_{}".format(self.get_random_suffix()),
            "title": "柳叶刀",
            "medical_device_cate_id": 60030003,
            "serial_no": "TEST03420352_{}".format(self.get_random_suffix()),
            "type_spec": "BN3004",
            "service_life": 3,
            "performer_id": performer.id,
            "responsible_dept_id": self.dept.id,
            "use_dept_id": use_department.id,
            "production_date": "2018-09-12",
            "bar_code": "123123123_{}".format(self.get_random_suffix()),
            "status": "US",
            "storage_place_id": 50020005,
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
            "storage_place_id": 50020005,
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



