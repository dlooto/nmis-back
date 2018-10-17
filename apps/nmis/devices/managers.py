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
            logger.info(e)
            return None

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


