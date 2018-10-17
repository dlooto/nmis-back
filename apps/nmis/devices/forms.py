# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from base.forms import BaseForm
from nmis.devices.consts import ASSERT_DEVICE_STATUS_CHOICES, ASSERT_DEVICE_CATE_CHOICES
from nmis.devices.models import AssertDevice, FaultType, RepairOrder
from utils.times import now
from nmis.hospitals.models import Staff


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

        assert_data = {
            'creator': self.creator,
            'assert_no': self.data.get('assert_no', '').strip(),
            'title': self.data.get('title', '').strip(),
            'medical_device_cate_id': self.data.get('medical_device_cate_id'),
            'serial_no': self.data.get('serial_no', '').strip(),
            'type_spec': self.data.get('type_spec', '').strip(),
            'service_life': self.data.get('service_life'),
            'production_date': self.data.get('production_date', '').strip(),
            'status': self.data.get('status', '').strip(),
            'storage_place_id': self.data.get('storage_place_id'),
            'purchase_date': self.data.get('purchase_date', '').strip(),
            'cate': self.data.get('cate', '').strip(),
        }

        if self.data.get('bar_code', '').strip():
            assert_data['bar_code'] = self.data.get('bar_code', '').strip()
        if self.data.get('performer_id'):
            assert_data['performer_id'] = self.data.get('performer_id')
        if self.data.get('responsible_dept_id'):
            assert_data['responsible_dept_id'] = self.data.get('responsible_dept_id')
        if self.data.get('use_dept_id'):
            assert_data['use_dept_id'] = self.data.get('use_dept_id')

        assert_device = AssertDevice.objects.create_assert_device(**assert_data)
        assert_device.cache()
        return assert_device


class AssertDeviceUpdateForm(BaseForm):

    def __init__(self, data, modifier, assert_device, *args, **kwargs):
        BaseForm.__init__(self, data, modifier, assert_device, *args, **kwargs)
        self.modifier = modifier
        self.assert_device = assert_device

        self.ERR_CODES.update(
            {
                'service_life_err': '预计使用年限类型错误',
                'status_err': '资产状态错误',
                'assert_no_err': '资产编号已存在',
                'serial_no_err': '资产序列号已存在',
                'bar_code_err': '设备条形码已存在',
            }
        )

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
        if service_life:
            if not isinstance(service_life, int):
                self.update_errors('service_life', 'service_life_err')
                return False
        return True

    def check_status(self):
        """
        校验资产设备状态
        """
        status = self.data.get('status', '').strip()
        if status:
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
        if assert_no:
            assert_device = AssertDevice.objects.get_assert_device_by_assert_no(assert_no)
            if assert_device and not self.assert_device == assert_device:
                self.update_errors('assert_no', 'assert_no_err')
                return False
        return True

    def check_serial_no(self):
        """
        校验是否存在相同的资产序列号
        """
        serial_no = self.data.get('serial_no', '').strip()
        if serial_no:
            assert_device = AssertDevice.objects.get_assert_device_by_serial_no(serial_no)
            if assert_device and not self.assert_device == assert_device:
                self.update_errors('serial_no', 'serial_no_err')
                return False
        return True

    def check_bar_code(self):
        """
        存在设备条形码时，校验是否存在相同的设备条形码
        """
        bar_code = self.data.get('bar_code', '').strip()
        if bar_code:
            if bar_code:
                assert_device = AssertDevice.objects.get_assert_device_by_bar_code(bar_code)
                if assert_device and not self.assert_device == assert_device:
                    self.update_errors('bar_code', 'bar_code_err')
                    return False
        return True

    def save(self):
        update_data = {
            'modifier': self.modifier,
            'modified_time': now(),
        }
        if self.data.get('bar_code', '').strip():
            update_data['bar_code'] = self.data.get('bar_code', '').strip()
        if self.data.get('performer_id'):
            update_data['performer_id'] = self.data.get('performer_id')
        if self.data.get('responsible_dept_id'):
            update_data['responsible_dept_id'] = self.data.get('responsible_dept_id')
        if self.data.get('use_dept_id'):
            update_data['use_dept_id'] = self.data.get('use_dept_id')
        if self.data.get('assert_no', '').strip():
            update_data['assert_no'] = self.data.get('assert_no')
        if self.data.get('title', '').strip():
            update_data['title'] = self.data.get('title', '').strip()
        if self.data.get('medical_device_cate_id'):
            update_data['medical_device_cate_id'] = self.data.get('medical_device_cate_id')
        if self.data.get('serial_no', '').strip():
            update_data['serial_no'] = self.data.get('serial_no', '').strip()
        if self.data.get('type_spec', '').strip():
            update_data['type_spec'] = self.data.get('type_spec', '').strip()
        if self.data.get('service_life'):
            update_data['service_life'] = self.data.get('service_life')
        if self.data.get('production_date', '').strip():
            update_data['production_date'] = self.data.get('production_date', '').strip()
        if self.data.get('status', '').strip():
            update_data['status'] = self.data.get('status', '').strip()
        if self.data.get('storage_place_id'):
            update_data['storage_place_id'] = self.data.get('storage_place_id')
        if self.data.get('purchase_date', '').strip():
            update_data['purchase_date'] = self.data.get('purchase_date', '').strip()

        return AssertDevice.objects.update_assert_device(self.assert_device, **update_data)


class RepairOrderCreateForm(BaseForm):

    def __init__(self, user_profile, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.user_profile = user_profile
        self.data = data

    ERR_CODES = {

    }

    def is_valid(self):
        return True

    def save(self):
        applicant_id = self.data.get('applicant_id')
        fault_type_id = self.data.get('fault_type_id')
        desc = self.data.get('desc').strip()
        applicant = Staff.objects.get_by_id(applicant_id)
        fault_type = FaultType.objects.get_by_id(fault_type_id)
        return RepairOrder.objects.create_order(applicant, fault_type, desc, self.user_profile)
