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


class AssertDeviceManager(BaseManager):

    def create(self):
        pass


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
                seq: Sequence = Sequence.objects.select_for_update().get(seq_code=REPAIR_ORDER_NO_SEQ_CODE)
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


