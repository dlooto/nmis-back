# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from django.db import transaction

from base.models import BaseManager
from nmis.devices.consts import REPAIR_ORDER_NO_SEQ_CODE, REPAIR_ORDER_NO_PREFIX, REPAIR_ORDER_NO_SEQ_DIGITS
from nmis.hospitals.models import Sequence
from utils import times

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

    def get_assert_devices(self, cate=None, search_key=None, status=None, storage_place=None):
        """
        资产设备列表
        :param search_key: 关键字：设备名
        :param status: 资产设备状态
        :param storage_place: 设备存储地点
        """
        assert_devices = self.filter()

        if cate:
            assert_devices = self.filter(cate=cate)
        if search_key:
            assert_devices = assert_devices.filter(title__contains=search_key)
        if status:
            assert_devices = assert_devices.filter(status__contains=status)
        if storage_place:
            assert_devices = assert_devices.filter(storage_place=storage_place)
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

    def create_order(self, applicant, fault_type, desc, creator):
        """
        :param applicant:
        :param fault_type:
        :param desc:
        :param creator:
        :return: 返回(boolean, RepairOrder对象/string)元祖
        """

        try:
            with transaction.atomic():
                seq = Sequence.objects.select_for_update().get(seq_code=REPAIR_ORDER_NO_SEQ_CODE)
                seq.curr_value()
                next_value = seq.next_value()
                timestamp = times.datetime_to_str(times.now(), format='%Y%m%d')
                order_no = RepairOrderManager.gen_repair_order_no(REPAIR_ORDER_NO_PREFIX, timestamp, next_value, seq_max_digits=REPAIR_ORDER_NO_SEQ_DIGITS)
                if not order_no:
                    return False, '生成编号异常'
                repair_order = self.create(
                    order_no=order_no, applicant=applicant, fault_type=fault_type,
                    desc=desc, creator=creator
                )
                seq.seq_value = next_value
                seq.save()
                seq.cache()
                return True, repair_order
        except Exception as e:
            logger.exception(e)
            return False, '创建报修单异常'

    @staticmethod
    def gen_repair_order_no(prefix, timestamp, seq, seq_max_digits=2):
        """
        :param prefix: 报修单号前缀
        :param timestamp: 时间戳字符串
        :param seq: 序列值
        :param seq_max_digits: 序列最大位数
        :return: 报修单号字符串： 前缀 + 时间戳 + 序列
        """
        # 默认支持的最大位数
        default_max_digits = 9

        if seq_max_digits > default_max_digits:
            return None

        seq_digits = len(str(seq))
        if seq_digits > seq_max_digits:
            return None
        seq_str = str(seq)
        if seq_digits < seq_max_digits:
            seq_str = "%s%s" % (str(10**seq_max_digits)[(seq_digits-seq_max_digits):], seq_str)

        order_no = "%s%s%s" % (prefix, timestamp, seq_str)
        return order_no


class MaintenancePlanManager(BaseManager):

    def create(self):
        pass


class FaultSolutionManager(BaseManager):

    def create(self):
        pass


