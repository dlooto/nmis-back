# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from base.models import BaseManager

logger = logging.getLogger(__name__)


class MedicalDeviceSix8CateManager(BaseManager):

    def create(self):
        pass

    def get_medical_device_six8_cates(self):
        """
        获取医疗器械分类列表
        """
        return self.exclude(parent=None)


class AssertDeviceManager(BaseManager):

    def create_assert_device(self, **data):
        """
        新建资产设备
        :param data: 资产设备数据dict
        :return:
        """
        try:
            return self.create(**data)
        except Exception as e:
            logger.exception(e)
            return None

    def update_assert_device(self, assert_device, **data):
        """
        更新资产设备
        :param assert_device: 更新的资产设备
        :param data: 更新资产设备数据，dict类型
        :return:
        """
        try:

            if data.get('medical_device_cate_id'):
                assert_device.medical_device_cate_id = data.get('medical_device_cate_id')

            if data.get('use_dept_id'):
                assert_device.use_dept_id = data.get('use_dept_id')

            if data.get('responsible_dept_id'):
                assert_device.responsible_dept_id = data.get('responsible_dept_id')

            if data.get('performer_id'):
                assert_device.performer_id = data.get('performer_id')
            if data.get('storage_place_id'):
                assert_device.storage_place_id = data.get('storage_place_id')
            new_assert_device = assert_device.update(data)
            new_assert_device.cache()
            return new_assert_device
        except Exception as e:
            logger.exception(e)
            return None

    def get_assert_devices(self, search_key=None, status=None):
        """
        资产设备列表
        :param search_key: 关键字：设备名
        :param status: 资产设备状态
        """
        assert_devices = self.filter()
        if search_key:
            assert_devices = assert_devices.filter(title__contains=search_key)
        if status:
            assert_devices = assert_devices.filter(status__contains=status)

        return assert_devices

    def get_assert_device_by_assert_no(self, assert_no):
        """
        通过资产设备编号查询资产设备
        :param assert_no: 资产设备编号
        """
        return self.filter(assert_no=assert_no).first()

    def get_assert_device_by_serial_no(self, serial_no):
        """
        通过资产序列号查询资产设备
        :param serial_no:
        """
        return self.filter(serial_no=serial_no).first()

    def get_assert_device_by_bar_code(self, bar_code):
        """
        通过资产设备条形码查询资产设备
        :param bar_code: 资产设备条形码
        """
        return self.filter(bar_code=bar_code).first()


class FaultTypeManager(BaseManager):

    def create(self):
        pass


class RepairOrderManager(BaseManager):

    def create(self):
        pass

    def gen_repair_order_no(self):
        pass


class MaintenancePlanManager(BaseManager):

    def create(self):
        pass


class FaultSolutionManager(BaseManager):

    def create(self):
        pass


