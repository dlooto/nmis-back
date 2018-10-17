# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from base.forms import BaseForm
from nmis.devices.consts import ASSERT_DEVICE_STATUS_CHOICES, ASSERT_DEVICE_CATE_CHOICES
from nmis.devices.models import AssertDevice

logger = logging.getLogger(__name__)


class AssertDeviceCreateForm(BaseForm):

    """
    创建资产设备表单验证
    """
    def __init__(self, creator, data, *args, **kwargs):
        BaseForm.__init__(self, creator, data, *args, **kwargs)
        self.data = data
        self.creator = creator

        self.ERR_CODES.update({
            'service_life_err': '预计使用年限类型错误',
            'status_err': '资产状态错误',
            'assert_no_err': '资产编号已存在',
            'serial_no_err': '资产序列号已存在',
            'bar_code_err': '设备条形码已存在',
            'cate_err': '资产设备类型错误'
        })

    def is_valid(self):
        if not self.check_service_life() or not self.check_status()\
                or not self.check_assert_no() or not self.check_serial_no()\
                or not self.check_bar_code():
            return False
        return True

    def check_service_life(self):
        """
        校验资产设备预计使用年限数据类型
        """
        service_life = self.data.get('service_life')
        if not isinstance(service_life, int):
            self.update_errors('service_life', 'service_life_err')
            return False
        return True

    def check_status(self):
        """
        校验资产设备状态
        """
        status = self.data.get('status', '').strip()
        if status not in dict(ASSERT_DEVICE_STATUS_CHOICES):
            self.update_errors('status', 'status_err')
            return False
        return True

    def check_assert_no(self):
        """
        校验是否存在相同的资产编号
        :return:
        """
        assert_no = self.data.get('assert_no', '').strip()
        assert_device = AssertDevice.objects.get_assert_device_by_assert_no(assert_no)
        if assert_device:
            self.update_errors('assert_no', 'assert_no_err')
            return False
        return True

    def check_serial_no(self):
        """
        校验是否存在相同的资产序列号
        """
        serial_no = self.data.get('serial_no', '').strip()
        assert_device = AssertDevice.objects.get_assert_device_by_serial_no(serial_no)
        if assert_device:
            self.update_errors('serial_no', 'serial_no_err')
            return False
        return True

    def check_bar_code(self):
        """
        存在设备条形码时，校验是否存在相同的设备条形码
        """
        bar_code = self.data.get('bar_code', '').strip()
        if bar_code:
            assert_device = AssertDevice.objects.get_assert_device_by_bar_code(bar_code)
            if assert_device:
                self.update_errors('bar_code', 'bar_code_err')
                return False
        return True

    def check_cate(self):
        """
        校验资产设备类型
        """
        cate = self.data.get('cate', '').strip()
        if cate not in dict(ASSERT_DEVICE_CATE_CHOICES):
            self.update_errors('cate', 'cate_err')
            return False
        return True

    def save(self):
        # 添加创建人
        self.data['creator'] = self.creator

        return AssertDevice.objects.create_assert_device(**self.data)
