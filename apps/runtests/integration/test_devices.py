# coding=utf-8
#
# Created by zeng, on 2018/10/29
#

#

import logging

from runtests import BaseTestCase

from utils import times

logs = logging.getLogger(__name__)


class AssertDevicesApiTestCase(BaseTestCase):

    def test_create_assert_device(self):
        """
        API测试：新建资产设备（医疗设备/信息化设备）
        """
        api = '/api/v1/devices/create'

        self.login_with_username(self.user)

        medical_assert_device_data = {
            "assert_no": "TEST0007_{}".format(self.get_random_suffix()),
            "title": "电热煮沸消毒器",
            "medical_device_cate_id": 60020003,
            "serial_no": "TEST03420352",
            "type_spec": "BN3004",
            "service_life": 3,
            "performer_id": 40040001,
            "responsible_dept_id": 30030001,
            "use_dept_id": 30030001,
            "production_date": "2018-09-12",
            "bar_code": "test123123123",
            "status": "US",
            "storage_place_id": 50010005,
            "purchase_date": "2018-10-09",
            "cate": "ME"
        }

        information_assert_device_data = {
            "assert_no": "TEST0008",
            "title": "电热煮沸消毒器",
            "serial_no": "TEST03420353",
            "type_spec": "BN3004",
            "service_life": 3,
            "performer_id": 40040001,
            "responsible_dept_id": 30030001,
            "use_dept_id": 30030001,
            "production_date": "2018-09-12",
            "bar_code": "test123123124",
            "status": "US",
            "storage_place_id": 50010005,
            "purchase_date": "2018-10-09",
            "cate": "IN"
        }

        response = self.post(api, data=medical_assert_device_data)
        self.assert_response_success(response)
        medical_assert_device = response.get('assert_device')
        self.assertIsNotNone(response.get(medical_assert_device))
