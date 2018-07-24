# coding=utf-8
#
# Created by junn, on 2018/6/11
#

# 

import logging

from runtests import BaseTestCase
from runtests.common.mixins import ProjectPlanMixin

logs = logging.getLogger(__name__)


class OrderDeviceApiTestCase(BaseTestCase, ProjectPlanMixin):
    """
    项目管理相关APi测试
    """

    device_create_api = '/api/v1/projects/{}/devices/create'  # 为项目添加设备
    one_device_api = '/api/v1/projects/{}/devices/{}'      # 单个设备操作API接口

    def setUp(self):
        BaseTestCase.setUp(self)
        self.project = self.create_project(self.admin_staff, self.dept, title="新项目")

    def test_ordered_device_create(self):
        """
        为项目添加设备
        """
        self.login_with_username(self.user)
        project = self.project

        ordered_devices = project.get_hardware_devices()
        device_count = len(ordered_devices)

        data = {
            "name": "血压测试仪",
            "num":  2,
            "planned_price":  1500.5,
            "measure": "台",
            "type_spec": "Tenda-1301",
            "purpose": "程序员要测血压",
        }

        response = self.post(self.device_create_api.format(project.id), data=data)
        self.assert_response_success(response)

        result_device = response.get("device")
        self.assertIsNotNone(result_device)
        self.assertEquals(device_count+1, len(project.get_hardware_devices()))
        self.assertEquals(result_device.get('name'), data.get('name'))

    def test_ordered_device_update(self):
        """
        修改项目的单个设备信息
        """
        self.login_with_username(self.user)

        project = self.project
        old_device = project.get_hardware_devices()[0]

        data = {
            "name": "血压测试仪_%s" % self.get_random_suffix(),
            "num":  2,
            "planned_price":  1500.5,
            "measure": "台",
            "type_spec": "Tenda-1301",
            "purpose": "程序员要测血压",
        }

        response = self.put(self.one_device_api.format(project.id, old_device.id), data=data)
        self.assert_response_success(response)

        result_device = response.get("device")
        self.assertIsNotNone(result_device)
        self.assertNotEquals(result_device.get('name'), old_device.name)

    def test_ordered_device_delete(self):
        """
        删除项目的单个设备项
        """
        self.login_with_username(self.user)
        project = self.project
        old_device = project.get_hardware_devices()[0]
        devices_count = len(project.get_hardware_devices())
        device_type = {
            "device_type": "HW"
        }
        response = self.post(
            self.one_device_api.format(project.id, old_device.id), data=device_type
        )
        self.assert_response_success(response)
        self.assertEquals(devices_count-1, len(project.get_hardware_devices()))
