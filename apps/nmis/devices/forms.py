# coding=utf-8
#
# Created by gong, on 2018-10-16
#

import logging

from base.forms import BaseForm
from nmis.devices.consts import ASSERT_DEVICE_STATUS_CHOICES, ASSERT_DEVICE_CATE_CHOICES, \
    MAINTENANCE_PLAN_TYPE_CHOICES, PRIORITY_CHOICES, ASSERT_DEVICE_CATE_INFORMATION, \
    ASSERT_DEVICE_CATE_MEDICAL
from nmis.devices.models import AssertDevice, FaultType, RepairOrder, MaintenancePlan, FaultSolution, MedicalDeviceSix8Cate
from utils import eggs
from utils.times import now, get_day_begin_time
from nmis.hospitals.models import Staff, Department, HospitalAddress

from collections import defaultdict


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
            'service_life_err':                 '预计使用年限类型错误',
            'status_err':                       '资产状态错误',
            'assert_no_err':                    '资产编号已存在',
            'serial_no_err':                    '资产序列号已存在',
            'bar_code_err':                     '设备条形码已存在',
            'cate_err':                         '资产设备类型错误',
            'medical_device_cate_null_err':     '医疗设备分类为空',
            'production_date_err':              '出厂日期{}: 大于当前日期',
        })

    def is_valid(self):
        if not self.check_service_life() or not self.check_status()\
                or not self.check_assert_no() or not self.check_serial_no()\
                or not self.check_bar_code() or not self.check_medical_device_cate()\
                or not self.check_production_date():
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

    def check_medical_device_cate(self):

        if self.data.get('cate') == ASSERT_DEVICE_CATE_MEDICAL:
            if not self.data.get('medical_device_cate_id'):
                self.update_errors('medical_device_cate', 'medical_device_cate_err')
                return False
        return True

    def check_production_date(self):
        production_date = self.data.get('production_date', '').strip()
        if production_date > now().strftime('%Y-%m-%d'):
            self.update_errors('production_date', 'production_date_err', production_date)
            return False
        return True

    def save(self):

        assert_data = {
            'creator': self.creator,
            'assert_no': self.data.get('assert_no', '').strip(),
            'title': self.data.get('title', '').strip(),
            'serial_no': self.data.get('serial_no', '').strip(),
            'type_spec': self.data.get('type_spec', '').strip(),
            'service_life': self.data.get('service_life'),
            'production_date': self.data.get('production_date', '').strip(),
            'status': self.data.get('status', '').strip(),
            'storage_place_id': self.data.get('storage_place_id'),
            'purchase_date': self.data.get('purchase_date', '').strip(),
            'cate': self.data.get('cate', '').strip(),
        }
        if self.data.get('cate', '').strip() == ASSERT_DEVICE_CATE_MEDICAL:
            assert_data['medical_device_cate_id'] = self.data.get('medical_device_cate_id')

        if self.data.get('bar_code', '').strip():
            assert_data['bar_code'] = self.data.get('bar_code', '').strip()
        if self.data.get('performer_id'):
            assert_data['performer_id'] = self.data.get('performer_id')
        if self.data.get('responsible_dept_id'):
            assert_data['responsible_dept_id'] = self.data.get('responsible_dept_id')
        if self.data.get('use_dept_id'):
            assert_data['use_dept_id'] = self.data.get('use_dept_id')
        if self.data.get('producer', '').strip():
            assert_data['producer'] = self.data.get('producer', '').strip()

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
            }
        )

    def is_valid(self):
        if not self.check_service_life() or not self.check_status()\
                or not self.check_assert_no() or not self.check_serial_no():
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

    def save(self):
        update_data = {
            'modifier': self.modifier,
            'modified_time': now(),
            'use_dept_id': self.data.get('use_dept_id'),
            'performer_id': self.data.get('performer_id'),
            'responsible_dept_id': self.data.get('responsible_dept_id'),
            'bar_code': self.data.get('bar_code', '').strip()

        }
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

        if self.data.get('producer') is not None:
            update_data['producer'] = self.data.get('producer', '').strip()

        return AssertDevice.objects.update_assert_device(self.assert_device, **update_data)


class RepairOrderCreateForm(BaseForm):

    def __init__(self, user_profile, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.user_profile = user_profile
        self.data = data
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'applicant_error': '申请人为空或数据错误',
            'fault_type_error': '故障类型为空或数据错误'
        })

    def is_valid(self):
        if not self.check_applicant() or not self.check_fault_type():
            return False
        return True

    def check_applicant(self):
        applicant_id = self.data.get('applicant_id')
        if not applicant_id:
            self.update_errors('applicant_id', 'applicant_error')
            return False
        try:
            applicant_id = int(applicant_id)
        except ValueError as e:
            logger.exception(e)
            self.update_errors('applicant_id', 'applicant_error')
            return False
        applicant = Staff.objects.get_by_id(applicant_id)
        if not applicant:
            self.update_errors('applicant_id', 'applicant_error')
            return False
        return True

    def check_fault_type(self):
        fault_type_id = self.data.get('fault_type_id')
        if not fault_type_id:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        try:
            fault_type_id = int(fault_type_id)
        except ValueError as e:
            logger.exception(e)
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        fault_type = FaultType.objects.get_cached(fault_type_id)
        if not fault_type:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        return True

    def save(self):
        applicant_id = self.data.get('applicant_id')
        fault_type_id = self.data.get('fault_type_id')
        desc = self.data.get('desc', '').strip()
        applicant = Staff.objects.get_by_id(applicant_id)
        fault_type = FaultType.objects.get_by_id(fault_type_id)
        return RepairOrder.objects.create_order(applicant, fault_type, desc, self.user_profile)


class RepairOrderDispatchForm(BaseForm):

    def __init__(self, user_profile, repair_order, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.repair_order = repair_order
        self.user_profile = user_profile
        self.data = data
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'priority_error': '优先级为空或数据错误',
            'maintainer_error': '维修工为空或数据错误',
        })

    def is_valid(self):
        if not self.check_maintainer() or not self.check_priority():
            return False
        return True

    def check_priority(self):
        priority = self.data.get('priority', '').strip()
        if not priority or priority not in dict(PRIORITY_CHOICES):
            self.update_errors('priority', 'priority_error')
            return False
        return True

    def check_maintainer(self):
        maintainer_id = self.data.get('maintainer_id')
        if not maintainer_id:
            self.update_errors('maintainer_id', 'maintainer_error')
            return False
        try:
            maintainer_id = int(maintainer_id)
        except ValueError as e:
            logger.exception(e)
            self.update_errors('maintainer_id', 'maintainer_error')
            return False
        maintainer = Staff.objects.get_by_id(maintainer_id)
        if not maintainer:
            self.update_errors('maintainer_id', 'maintainer_error')
            return False
        return True

    def save(self):
        maintainer = Staff.objects.get_by_id(self.data.get('maintainer_id'))
        priority = self.data.get('priority')
        return RepairOrder.objects.dispatch_repair_order(self.repair_order, self.user_profile, maintainer, priority)


class RepairOrderHandleForm(BaseForm):

    def __init__(self, user_profile, repair_order, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.repair_order = repair_order
        self.user_profile = user_profile
        self.data = data
        self.files = kwargs.get('files')
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'result_error': '处理结果为空或数据错误',
            'expenses_error': '维修费用为空或数据错误',
            'files_error': '文件名和文件路径不能为空',
            'solution_error': '为空或数据错误',
            'repair_devices_error': '设备id为空或异常',
        })

    def is_valid(self):
        if not self.check_result():
            return False
        # 校验非必传参数
        if self.data.get('expenses') and not self.check_expenses():
            return False
        if self.data.get('repair_devices') and not self.check_repair_devices():
            return False
        return True

    def check_result(self):
        result = self.data.get('result', '').strip()
        if not result:
            self.update_errors('result', 'result_error')
            return False
        return True

    def check_expenses(self):
        expenses = self.data.get('expenses')
        try:
            int(expenses)
        except ValueError as e:
            self.update_errors('expenses', 'expenses_error')
            return False
        return True

    def check_repair_devices(self):
        assert_devices_data = self.data.get('repair_devices')
        for device in assert_devices_data:
            if not device.get('id'):
                self.update_errors('repair_devices', 'repair_devices_error')
                return False
            try:
                int(device.get('id'))
            except ValueError as e:
                logger.exception(e)
                self.update_errors('repair_devices', 'repair_devices_error')
                return False
        assert_devices = AssertDevice.objects.filter(id__in=[item.get('id') for item in assert_devices_data]).all()
        if len(assert_devices_data) > len(assert_devices):
            self.update_errors('repair_devices', 'repair_devices_error')
            return False
        return True

    def save(self):
        result = self.data.get('result').strip()
        update_data = dict()
        if self.data.get('expenses'):
            update_data['expenses'] = self.data.get('expenses')
        if self.files:
            files_ids_str = ','.join('%d' % file.id for file in self.files)
            update_data['files'] = files_ids_str
        repair_devices_data = self.data.get('repair_devices')
        if repair_devices_data:
            repair_devices = AssertDevice.objects.filter(id__in=[item.get('id') for item in repair_devices_data]).all()
            update_data['repair_devices'] = repair_devices
        return RepairOrder.objects.handle_repair_order(self.repair_order, self.user_profile, result, **update_data)


class RepairOrderCommentForm(BaseForm):

    def __init__(self, user_profile, repair_order, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.repair_order = repair_order
        self.user_profile = user_profile
        self.data = data
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'comment_grade_error': '评论等级为空或数据错误',
            'comment_content_error': '评论内容数据错误'
        })

    def is_valid(self):
        if not self.check_comment_grade():
            return False
        if self.data.get('comment_content') and not self.check_comment_content():
            return False
        return True

    def check_comment_grade(self):
        comment_grade = self.data.get('comment_grade')
        if not comment_grade:
            self.update_errors('comment_grade', 'comment_grade_error')
            return False
        try:
            comment_grade = int(comment_grade)
        except ValueError as e:
            self.update_errors('comment_grade', 'comment_grade_error')
            return False
        grades = [grade for grade in range(1, 6)]
        if comment_grade not in grades:
            self.update_errors('comment_grade1', 'comment_grade_error')
            return False
        return True

    def check_comment_content(self):
        comment_content = self.data.get('comment_content', '').strip()
        if len(comment_content) > 127:
            self.update_errors('comment_content', 'comment_content_error')
        return True

    def save(self):
        comment_grade = self.data.get('comment_grade')
        comment_content = self.data.get('comment_content')
        update_data = {"comment_grade": comment_grade}

        if comment_content is not None:
            update_data.update({"comment_content": comment_content.strip()})

        return RepairOrder.objects.comment_repair_order(self.repair_order, self.user_profile, **update_data)


class MaintenancePlanCreateForm(BaseForm):

    def __init__(self, data, storage_places, assert_devices, executor, creator, *args, **kwargs):
        BaseForm.__init__(self, data, storage_places, assert_devices, executor, creator, *args, **kwargs)

        self.storage_places = storage_places
        self.assert_devices = assert_devices
        self.executor = executor
        self.creator = creator

        self.ERR_CODES.update(
            {
                'type_err': '维护类型错误',
                'date_err': '开始日期大于了结束日期',
                'expired_date_format_err': '{}: 日期格式错误',
                'start_date_format_err': '{}: 日期格式错误',
                'start_date_err': '{}: 小于当前日期',
                'expired_date_err': '{}: 小于当前日期'
            }
        )

    def is_valid(self):
        if not self.check_type() or not self.check_date():
            return False
        return True

    def check_type(self):
        maintenance_plan_type = self.data.get('type')
        if maintenance_plan_type not in dict(MAINTENANCE_PLAN_TYPE_CHOICES):
            self.update_errors('type', 'type_err')
            return False
        return True

    def check_date(self):
        """
        校验维护计划的开始日期和结束日期
        """
        start_date = self.data.get('start_date', '').strip()
        expired_date = self.data.get('expired_date', '').strip()
        if not eggs.check_day(start_date):
            logger.info(get_day_begin_time(now()))
            self.update_errors('date_err', 'start_date_format_err', start_date)
            return False
        if not eggs.check_day(expired_date):
            logger.info(expired_date)
            self.update_errors('date_err', 'expired_date_format_err', expired_date)
            return False
        if start_date < now().strftime('%Y-%m-%d'):
            self.update_errors('date_err', 'start_date_err', start_date)
            return False
        if expired_date < now().strftime('%Y-%m-%d'):
            self.update_errors('date_err', 'expired_date_err', expired_date)
            return False
        if start_date > expired_date:
            self.update_errors('date', 'date_err')
            return False

        return True

    def save(self):
        logger.info(self.data.get('start_date', '').strip())
        maintenance_plan_data = {
            'title': self.data.get('title', '').strip(),
            'type': self.data.get('type', '').strip(),
            'start_date': self.data.get('start_date', '').strip(),
            'expired_date': self.data.get('expired_date', '').strip(),
            'executor': self.executor,
            'creator': self.creator
        }
        return MaintenancePlan.objects.create_maintenance_plan(
            self.storage_places, self.assert_devices, **maintenance_plan_data)


class FaultSolutionCreateForm(BaseForm):

    def __init__(self, user_profile, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.user_profile = user_profile
        self.files = kwargs.get('files')
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'title_error': '标题为空或数据错误',
            'title_exists': '已存在相同标题数据',
            'fault_type_error': '故障类型为空或数据错误',
            'solution_error': '解决方案为空或数据错误',
            'desc_error': '详情描述为空或数据错误',
        })

    def is_valid(self):
        if not self.check_title() or not self.check_fault_type() or not self.check_solution():
            return False
        return True

    def check_title(self):
        if not self.data.get('title', '').strip():
            self.update_errors('title', 'title_error')
            return False
        fs = FaultSolution.objects.filter(title=self.data.get('title', '').strip())
        if fs.first():
            self.update_errors('title', 'title_exists')
            return False
        return True

    def check_desc(self):
        if not self.data.get('desc', '').strip():
            self.update_errors('desc', 'desc_error')
            return False
        return True

    def check_fault_type(self):
        fault_type_id = self.data.get('fault_type_id')
        if not fault_type_id:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        try:
            int(fault_type_id)
        except ValueError as e:
            logger.exception(e)
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        fault_type = FaultType.objects.get_cached(fault_type_id)
        if not fault_type:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False

        return True

    def check_solution(self):
        if not self.data.get('solution', '').strip():
            self.update_errors('solution', 'solution_error')
            return False
        return True

    def save(self):
        title = self.data.get('title', '').strip()
        fault_type_id = self.data.get('fault_type_id')
        fault_type = FaultType.objects.get_cached(fault_type_id)
        solution = self.data.get('solution')
        update_data = dict()
        if self.data.get('desc') is not None:
            update_data['desc'] = self.data.get('desc', '').strip()
        if self.files:
            files_ids_str = ','.join('%d' % file.id for file in self.files)
            update_data['files'] = files_ids_str
        return FaultSolution.objects.create_fault_solution(
            self.user_profile, title, fault_type, solution, **update_data
        )


class FaultSolutionUpdateForm(BaseForm):

    def __init__(self, user_profile, fault_solution, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.user_profile = user_profile
        self.fault_solution = fault_solution
        self.files = kwargs.get('files')
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'title_error': '标题为空或数据错误',
            'title_exists': '已存在相同标题数据',
            'fault_type_error': '故障类型为空或数据错误',
            'solution_error': '解决方案为空或数据错误',
            'desc_error': '详情描述为空或数据错误',
        })

    def is_valid(self):
        if not self.check_title() or not self.check_fault_type() or not self.check_solution():
            return False
        return True

    def check_title(self):
        if not self.data.get('title', '').strip():
            self.update_errors('title', 'title_error')
            return False
        fs = FaultSolution.objects.filter(title=self.data.get('title', '').strip())
        if fs.first():
            self.update_errors('title', 'title_exists')
            return False
        return True

    def check_desc(self):
        if not self.data.get('desc', '').strip():
            self.update_errors('desc', 'desc_error')
            return False
        return True

    def check_fault_type(self):
        fault_type_id = self.data.get('fault_type_id')
        if not fault_type_id:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        try:
            int(fault_type_id)
        except ValueError as e:
            logger.exception(e)
            self.update_errors('fault_type_id', 'fault_type_error')
            return False
        fault_type = FaultType.objects.get_cached(fault_type_id)
        if not fault_type:
            self.update_errors('fault_type_id', 'fault_type_error')
            return False

        return True

    def check_solution(self):
        if not self.data.get('solution', '').strip():
            self.update_errors('solution', 'solution_error')
            return False
        return True

    def save(self):
        title = self.data.get('title', '').strip()
        fault_type_id = self.data.get('fault_type_id')
        fault_type = FaultType.objects.get_cached(fault_type_id)
        solution = self.data.get('solution')
        update_data = dict()
        if self.data.get('desc') is not None:
            update_data['desc'] = self.data.get('desc', '').strip()
        if self.files:
            files_ids_str = ','.join('%d' % file.id for file in self.files)
            update_data['files'] = files_ids_str
        return FaultSolution.objects.update_fault_solution(
            self.fault_solution, self.user_profile, title, fault_type, solution, **update_data
        )


class AssertDeviceBatchUploadForm(BaseForm):
    """
    批量导入资产设备表单验证
    """

    def __init__(self, data, creator, cate, *args, **kwargs):
        BaseForm.__init__(self, data, creator, cate, *args, **kwargs)
        self.creator = creator
        self.cate = cate
        self.default_dict = defaultdict(list)
        self.performer_list = None
        self.use_dept_list = None
        self.res_dept_list = None
        self.storage_place_list = None
        self.medical_device_cate_list = None

        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'assert_no_err':                '{}: 已存在系统中',
            'assert_no_repeat_err':         '表中存在相同项的资产设备编号',
            'assert_no_null_err':           '{}行: 资产设别编号为空',
            'serial_no_err':                '{}: 已存在系统中',
            'serial_no_repeat_err':         '表中存在相同项的资产设备序列号',
            'serial_no_null_err':           '{}: 资产设备序列号为空',
            'use_dept_err':                 '{}: 系统不存在此使用部门信息',
            'performer_err':                '{}: 系统不存在此负责人信息',
            'resp_dept_err':                '{}: 系统不存在此负责部门信息',
            'storage_place_err':            '{}: 系统不存在此存储地点信息',
            'medical_code_err':             '{}: 系统不存在此医疗分类编号信息',
            'medical_code_null_err':        '医疗分类编号不能为空值',
            'medical_device_cate_err':      '医疗设备分类不能为空',
            'type_spec_null_err':           '资产设备规格型号不能为空',
            'production_date_null_err':     '资产设备出厂日期不能为空',
            'purchase_date_err':            '资产设备购入日期不能为空',
            'status_err':                   '{}: 和定义的资产设备状态不一致',
            'status_null_err':              '资产设备状态不能为空',
            'service_life_null_err':        '使用年限不能为空',
            'service_life_data_type_err':   '使用年限数据类型错误',
            'assert_title_err':             '{}行: 资产设备名称为空'
        })

    def is_valid(self):
        if not self.check_medical_device_cate() or not self.check_serial_no()\
                or not self.check_performer() or not self.check_medical_code()\
                or not self.check_use_dept() or not self.check_responsible_dept()\
                or not self.check_storage_place() or not self.check_assert_no()\
                or not self.check_type_spec() or not self.check_production_date()\
                or not self.check_purchase_date() or not self.check_status()\
                or not self.check_service_life() or not self.check_assert_title():
            return False
        return True

    def check_assert_title(self):

        for row_data in self.data:

            if not row_data.get('title', '').strip():
                self.update_errors('assert_title', 'assert_title_err', self.data.index(row_data)+2)
                return False
        return True

    def check_assert_no(self):
        assert_no_list = []
        for row_data in self.data:
            assert_no = row_data.get('assert_no', '').strip()
            if not assert_no:
                self.update_errors('assert_no', 'assert_no_null_err', self.data.index(row_data)+2)
                return False
            assert_no_list.append(assert_no)

        if not len(set(assert_no_list)) == len(assert_no_list):
            self.update_errors('assert_no', 'assert_no_repeat_err')
            return False

        assert_devices = AssertDevice.objects.filter(assert_no__in=assert_no_list)
        assert_no_db_list = [assert_device.assert_no for assert_device in assert_devices]

        for assert_no in assert_no_list:
            if assert_no in assert_no_db_list:
                self.update_errors('assert_no', 'assert_no_err', assert_no)
                return False
        return True

    def check_serial_no(self):
        serial_no_list = []
        for row_data in self.data:
            if not row_data.get('serial_no', '').strip():
                self.update_errors('serial_no', 'serial_no_null_err', self.data.index(row_data)+2)
                return False
            serial_no_list.append(row_data.get('serial_no'))

        if not len(set(serial_no_list)) == len(serial_no_list):
            self.update_errors('serial_no', 'serial_no_repeat_err')
            return False
        # 校验数据库中属否存在相关序列号信息
        assert_devices = AssertDevice.objects.filter(serial_no__in=serial_no_list)
        assert_device_serial_no = [assert_device.serial_no for assert_device in assert_devices]

        for serial_no in serial_no_list:
            if serial_no in assert_device_serial_no:
                self.update_errors('serial_no', 'serial_no_err', serial_no)
                return False
        return True

    def check_use_dept(self):
        use_dept_list = []
        for row_data in self.data:
            use_dept_list.append(row_data.get('use_dept', '').strip())
        use_dept_db_list = Department.objects.filter(name__in=set(use_dept_list))
        use_dept_names = [dept_db.name for dept_db in use_dept_db_list]

        if not len(set(use_dept_list)) == len(use_dept_db_list):
            for dept in use_dept_list:
                if dept not in use_dept_names:
                    self.update_errors('use_dept', 'use_dept_err', dept)
                    return False
        self.use_dept_list = use_dept_db_list
        return True

    def check_performer(self):
        performer_list = []
        for row_data in self.data:
            performer_list.append(row_data.get('performer', '').strip())
        performer_db_list = Staff.objects.filter(name__in=set(performer_list))
        performer_names = [performer_db.name for performer_db in performer_db_list]

        if not len(set(performer_list)) == len(performer_names):
            for performer_name in performer_list:
                if performer_name not in performer_names:
                    self.update_errors('performer', 'performer_err', performer_name)
            return False
        self.performer_list = performer_db_list
        return True

    def check_responsible_dept(self):
        # 检验数据库是否存在相关负责部门信息
        res_dept_list = []
        for row_data in self.data:
            res_dept_list.append(row_data.get('responsible_dept', '').strip())
        resp_dept_db_list = Department.objects.filter(name__in=set(res_dept_list))
        resp_dept_db_names = [resp_dept_db.name for resp_dept_db in resp_dept_db_list]

        if not len(set(res_dept_list)) == len(resp_dept_db_names):
            for dept_name in res_dept_list:
                if dept_name not in resp_dept_db_names:
                    self.update_errors('resp_dept', 'resp_dept_err', dept_name)
                    return False
        self.res_dept_list = resp_dept_db_list
        return True

    def check_medical_code(self):
        # 检验数据库中是否存在医院68码分类编号相关信息
        if self.cate == ASSERT_DEVICE_CATE_INFORMATION:
            return True
        code_list = []
        for row_data in self.data:
            code_list.append(row_data.get('code', '').strip())

        if not len(code_list) == len(self.data):
            self.update_errors('medical_code', 'medical_code_null_err')
            return False

        medical_device_cate_db_list = MedicalDeviceSix8Cate.objects.exclude(parent=None).filter(code__in=set(code_list))

        medical_device_cate_db_codes = [
            medical_device_cate.code for medical_device_cate in medical_device_cate_db_list
        ]

        if not len(set(code_list)) == len(medical_device_cate_db_codes):
            for code in set(code_list):
                if code not in medical_device_cate_db_codes:
                    self.update_errors('medical_code', 'medical_code_err', code)
            return False

        self.medical_device_cate_list = medical_device_cate_db_list
        return True

    def check_medical_device_cate(self):
        # 校验医疗分类类型
        if self.cate == ASSERT_DEVICE_CATE_INFORMATION:
            return True
        medical_device_cate_list = []
        for row_data in self.data:
            medical_device_cate_list.append(row_data.get('medical_device_cate', '').strip())
        if not len(medical_device_cate_list) == len(self.data):
            self.update_errors('medical_device_cate', 'medical_device_cate_err')
            return False
        return True

    def check_storage_place(self):

        # 检验数据库中是否存在存储地点相关信息
        storage_place_list = []
        for row_data in self.data:
            storage_place_list.append(row_data.get('storage_place', '').strip())
        storage_place_db_list = HospitalAddress.objects.exclude(parent=None).filter(title__in=set(storage_place_list))
        storage_place_titles = [storage_place_db.title for storage_place_db in storage_place_db_list]

        if not len(set(storage_place_list)) == len(storage_place_titles):
            for storage_place_title in storage_place_list:
                if storage_place_title not in storage_place_titles:
                    self.update_errors('storage_place', 'storage_place_err', storage_place_title)
                    return False
        self.storage_place_list = storage_place_db_list
        return True

    def check_type_spec(self):
        for row_data in self.data:
            if not row_data.get('type_spec', '').strip():
                self.update_errors('type_spec', 'type_spec_null_err')
                return False
        return True

    def check_production_date(self):
        for row_data in self.data:
            if not row_data.get('production_date', '').strip():
                self.update_errors('production_date', 'production_date_null_err')
                return False
        return True

    def check_purchase_date(self):
        for row_data in self.data:
            if not row_data.get('purchase_date', '').strip():
                self.update_errors('purchase_date', 'purchase_date_err')
                return False
        return True

    def check_status(self):

        for row_data in self.data:
            status = row_data.get('status', '').strip()
            if not status:
                self.update_errors('status', 'status_null_err')
                return False
            if status not in dict(ASSERT_DEVICE_STATUS_CHOICES).values():
                self.update_errors('status', 'status_err', status)
                return False
        return True

    def check_service_life(self):
        for row_data in self.data:
            if not row_data.get('service_life'):
                self.update_errors('service_life', 'service_life_null_err')
                return False
            # if not isinstance(row_data.get('service_life'), int):
            #     self.update_errors('service_life', 'service_life_data_type_err')
            #     return False
        return True

    def save(self):
        assert_devices = []
        for row_data in self.data:
            for key, value in dict(ASSERT_DEVICE_STATUS_CHOICES).items():
                if row_data['status'] == value:
                    row_data['status'] = key
                    break
            for performer in self.performer_list:
                if row_data.get('performer', '').strip() == performer.name:
                    row_data['performer'] = performer

            for use_dept in self.use_dept_list:
                if row_data.get('use_dept', '').strip() == use_dept.name:
                    row_data['use_dept'] = use_dept

            for resp_dept in self.res_dept_list:
                if row_data.get('responsible_dept', '').strip() == resp_dept.name:
                    row_data['responsible_dept'] = resp_dept

            for storage_place in self.storage_place_list:
                if row_data.get('storage_place', '').strip() == storage_place.title:
                    row_data['storage_place'] = storage_place

            if self.cate == ASSERT_DEVICE_CATE_MEDICAL:
                for medical_device_code in self.medical_device_cate_list:
                    if row_data.get('code', '').strip() == medical_device_code.code:
                        row_data['medical_device_cate'] = medical_device_code
                del row_data['code']
            row_data['creator'] = self.creator
            row_data['cate'] = self.cate
            assert_devices.append(
                AssertDevice(**row_data)
            )
        return AssertDevice.objects.bulk_create_assert_device(assert_devices)


class FaultSolutionsImportForm(BaseForm):

    def __init__(self, user_profile, data, *args, **kwargs):
        BaseForm.__init__(self, data, args, kwargs)
        self.user_profile = user_profile
        self.pre_data = self.init_check_data()
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'title_error': '第{0}行: 标题为空或数据错误',
            'title_exists': '第{0}行: 已存在相同标题',
            'fault_type_error': '第{0}行: 故障类型为空或数据错误',
            'fault_type_not_exists': '第{0}行: 故障类型不存在，请检查',
            'fault_type_not_in_setting':  '系统尚未设置故障类型，请联系管理员',
            'solution_error': '第{0}行: 解决方案为空或数据错误',
            'title_fault_type_exists': '第{0}行: 已存在相同故障类型的标题'
        })

    def init_check_data(self):
        """
        封装各列数据, 用以进行数据验证
        :return:
        """
        pre_data = dict()
        if self.data and self.data[0] and self.data[0][0]:
            titles, fault_type_titles, solutions = [], [], []
            for row_data in self.data[0]:
                titles.append(row_data.get('title', '').strip())
                fault_type_titles.append(row_data.get('fault_type_title', '').strip())
                solutions.append(row_data.get('solution', '').strip())
            pre_data['titles'] = titles
            pre_data['fault_type_titles'] = fault_type_titles
            pre_data['solutions'] = solutions
        return pre_data

    def is_valid(self):
        if not self.check_title() or not self.check_fault_type() or not self.check_solution() \
                or not self.check_title_fault_type_unique():
            return False
        return True

    def check_title(self):
        if self.pre_data.get('titles'):
            query_data = FaultSolution.objects.all().values_list('title')
            for index, title in enumerate(self.pre_data.get('titles')):
                if not title:
                    self.update_errors('title', 'title_error', index+1)
                    return False
                if (title,) in query_data:
                    self.update_errors('title', 'title_exists', index+1)
                    return False
        return True

    def check_fault_type(self):
        # 非空校验
        if self.pre_data.get('fault_type_titles'):
            queryset = FaultType.objects.all()
            if not queryset:
                self.update_errors('fault_type', 'fault_type_not_in_setting')
                return False
            fault_type_list = [item.get('title') for item in queryset.values('title')]

            for index, fault_type_title in enumerate(self.pre_data.get('fault_type_titles')):
                if not fault_type_title:
                    self.update_errors('fault_type', 'fault_type_error', index+1)
                    return False
                if fault_type_title not in fault_type_list:
                    self.update_errors('fault_type', 'fault_type_not_exists', index+1)
                    return False
        return True

    def check_solution(self):
        # 非空校验
        if self.pre_data.get('solutions'):
            for index, solution in enumerate(self.pre_data.get('solutions')):
                if not solution:
                    self.update_errors('solution', 'solution_error', index+1)
                    return False
        return True

    def check_title_fault_type_unique(self):
        """
        校验title和fault_type联合唯一性
        需先进行非空校验后进行该项校验
        :return:
        """
        if self.data and self.data[0]:
            query_data = FaultSolution.objects.all().values_list('title', 'fault_type__title')
            for index, row_data in enumerate(self.data[0]):
                if (row_data.get('title'), row_data.get('fault_type_title')) in query_data:
                    self.update_errors('unique', 'title_fault_type_exists', index+1)
                    return False
        return True

    def save(self):

        # 封装excel数据
        fault_solution_data = []
        if self.data and self.data[0] and self.data[0][0]:
            for row_data in self.data[0]:
                fault_solution_data.append({
                    'title': row_data.get('title', '').strip(),
                    'fault_type_title': row_data.get('fault_type_title', '').strip(),
                    'solution': row_data.get('solution', '').strip(),
                    'creator': self.user_profile,
                })
            fault_type_dict = dict()
            fault_type_titles = set(self.pre_data['fault_type_titles'])
            fault_types = FaultType.objects.filter(title__in=fault_type_titles)
            for ft in fault_types:
                fault_type_dict[ft.title] = ft

            for fs in fault_solution_data:
                fs['fault_type'] = fault_type_dict[fs['fault_type_title']]
                del fs['fault_type_title']
        return FaultSolution.objects.bulk_create_fault_solution(fault_solution_data)



