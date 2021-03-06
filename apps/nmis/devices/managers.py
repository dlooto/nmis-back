# coding=utf-8
#
# Created by gong, on 2018-10-16
#

import logging
import threading

from django.db import transaction
from django.db.models import Q, F

from base.models import BaseManager
from nmis.devices.consts import ASSERT_DEVICE_STATUS_USING, MAINTENANCE_PLAN_NO_PREFIX, \
    MAINTENANCE_PLAN_NO_SEQ_CODE, MAINTENANCE_PLAN_NO_SEQ_DIGITS, \
    REPAIR_ORDER_NO_SEQ_CODE, \
    REPAIR_ORDER_NO_PREFIX, REPAIR_ORDER_NO_SEQ_DIGITS, \
    REPAIR_ORDER_STATUS_DONE, REPAIR_ORDER_STATUS_CLOSED, REPAIR_ORDER_STATUS_DOING, \
    MAINTENANCE_PLAN_EXPIRED_DATE_ON_MONTH, MAINTENANCE_PLAN_EXPIRED_DATE_ON_WEEK, \
    MAINTENANCE_PLAN_EXPIRED_DATE_THREE_DAY, MAINTENANCE_PLAN_EXPIRED_DATE_NOW_DAY, \
    MAINTENANCE_PLAN_EXPIRED_DATE_BE_OVERDUE
from nmis.hospitals.models import Sequence
from utils import times

logger = logging.getLogger(__name__)


class MedicalDeviceCateManager(BaseManager):

    def create_medical_device_cate(self, creator, medical_device_cate):
        pass

    def get_medical_device_second_grade_cates(self, *args, **kwargs):
        """
        获取所有医疗器械二级产品分类列表
        """
        qs = self.filter(level=2)
        search = kwargs.get('search')
        if search is not None and isinstance(search, str):
            qs = qs.filter(Q(title__contains=search.strip()) | Q(code__contains=search.strip()))

        return qs.order_by('code')

    def get_med_dev_second_grade_cates_by_catalog(self, catalog_id):
        """
        根据分类目录ID获取医疗器械分类目录
        :return:
        """
        return self.select_related('parent__parent').filter(parent__parent__id=catalog_id, level=2).order_by('code')

    def get_med_dev_cate_catalogs(self):
        """
        获取医疗器械分类目录
        :return:
        """
        return self.filter(parent=None, level=0).order_by('code')

    def bulk_create_med_dev_cate(self, level, cates):
        """
        批量创建医疗器械分类

        :return:
        """
        # 0: 分类目录;1: 一级产品分类; 2: 二级产品分类
        if level not in [0, 1, 2]:
            return None
        objs = []

        if level == 0:
            for item in cates:
                objs.append(self.model(
                    title=item.get('title'),
                    code=item.get('level_code'),
                    level_code=item.get('level_code'),
                    level=0,
                    parent=None,
                    creator=item.get('creator'),
                ))
        if level == 1:
            for item in cates:
                objs.append(self.model(
                    title=item.get('title'),
                    code=item.get('code'),
                    level_code=item.get('level_code'),
                    level=1,
                    parent=item.get('parent'),
                    creator=item.get('creator'),
                ))
        if level == 2:
            for item in cates:
                objs.append(self.model(
                    title=item.get('title'),
                    code=item.get('code'),
                    level_code=item.get('level_code'),
                    level=2,
                    parent=item.get('parent'),
                    mgt_cate=item.get('mgt_cate'),
                    desc=item.get('desc'),
                    example=item.get('example'),
                    purpose=item.get('purpose'),
                    creator=item.get('creator'),
                ))
        db_catalogs = self.filter(code__in=[obj.code for obj in objs])
        if db_catalogs:
            for obj in objs[:]:
                if obj.code in [item.code for item in db_catalogs]:
                    objs.remove(obj)
        if not objs:
            return db_catalogs
        try:
            new_cates = self.bulk_create(objs)
            if level == 2:
                return cates
            return self.filter(code__in=[item.code for item in new_cates])
        except Exception as e:
            logger.exception(e)
            return None


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

            if data.get('use_dept_id') or data.get('use_dept_id') is None:
                assert_device.use_dept_id = data.get('use_dept_id')

            if data.get('responsible_dept_id') or data.get('responsible_dept_id') is None:
                assert_device.responsible_dept_id = data.get('responsible_dept_id')

            if data.get('performer_id') or data.get('performer_id') is None:
                assert_device.performer_id = data.get('performer_id')

            if data.get('storage_place_id'):
                assert_device.storage_place_id = data.get('storage_place_id')
            new_assert_device = assert_device.update(data)
            new_assert_device.cache()
            return new_assert_device
        except Exception as e:
            logger.exception(e)
            return None

    def get_assert_devices(self, cate=None, search_key=None, status=None, storage_places=None):
        """
        资产设备列表
        :param cate: 资产设备类型
        :param search_key: 关键字：设备名
        :param status: 资产设备状态
        :param storage_places: 设备存储地点
        """
        assert_devices = self.filter()

        if cate:
            assert_devices = self.filter(cate=cate)
        if search_key:
            assert_devices = assert_devices.filter(title__contains=search_key)
        if status:
            assert_devices = assert_devices.filter(status__in=status)
        if storage_places:
            assert_devices = assert_devices.filter(storage_place__in=storage_places)
        return assert_devices.order_by('-created_time')

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

    def get_assert_device_by_ids(self, device_ids):
        """
        通过资产设备ID集合查询资产设备
        :param device_ids: 资产设备ID list
        :return:
        """
        return self.filter(id__in=device_ids)

    def update_assert_devices_use_dept(self, assert_devices, use_dept):
        """
        单个或多个资产设备调配使用科室（调配之后资产设备状态变成使用中）
        :return:
        """
        try:
            with transaction.atomic():
                assert_devices.update(use_dept=use_dept, status=ASSERT_DEVICE_STATUS_USING)
                for assert_device in assert_devices:
                    assert_device.cache()
                return assert_devices
        except Exception as e:
            logger.exception(e)
            return None

    def bulk_create_assert_device(self, assert_devices):

        try:
            self.bulk_create(assert_devices)
            return True
        except Exception as e:
            logger.exception(e)
            return False


class FaultTypeManager(BaseManager):

    def create_fault_type(self, title, parent, creator, **not_required_data):
        ft_db = self.filter(parent=None).first()
        if not ft_db:
            logger.warning('init root node data not been set')
            return False, None
        if (not ft_db and parent) or (ft_db and not parent):
            return False, None

        try:
            new_ft = self.create(
                title=title, parent=parent, creator=creator, **not_required_data
            )
            return True, new_ft
        except Exception as e:
            logger.exception(e)
            return False, None

    def get_tree(self):
        all_fault_types = self.values(
            'id', 'title', 'desc', 'parent_id', 'sort', 'level',
        )
        if not all_fault_types:
            return None

        parent_ids = set()
        root_fault_type = None

        for ft in all_fault_types:
            parent_ids.add(ft.get('parent_id'))
            if not ft.get('parent_id'):
                root_fault_type = ft
        if not root_fault_type:
            logger.warning('root fault type not been set.')
            return None
        parents = []

        for ft in all_fault_types:
            if ft.get('id') in parent_ids:
                parents.append(ft)
                ft['has_children'] = True
            else:
                ft['has_children'] = False

        self.gen_tree(root_fault_type, all_fault_types)
        return root_fault_type

    def gen_tree(self, parent, fault_types):
        if not parent:
            return None
        if not parent.get('has_children'):
            parent['children'] = []
        else:
            children = []
            for item in fault_types:
                if item.get('parent_id') == parent.get('id'):
                    children.append(item)
                    parent['children'] = children
            for child in children:
                self.gen_tree(child, fault_types)

class RepairOrderManager(BaseManager):

    def create_order(self, applicant, fault_type, creator, *args, **kwargs):
        """
        创建报修单
        :param applicant: 申请人
        :param fault_type: 故障类型
        :param desc:    故障描述
        :param creator: 创建人
        :return: 返回(boolean, RepairOrder对象/string)元祖
        """
        lock = threading.RLock()
        try:
            with transaction.atomic():
                lock.acquire()
                seq = Sequence.objects.select_for_update().get(seq_code=REPAIR_ORDER_NO_SEQ_CODE)
                if not seq:
                    logger.warning('The sequence not exists')
                    return False, '序列未设置，请联系管理员'
                seq.curr_value()
                next_value = seq.next_value()
                timestamp = times.datetime_to_str(times.now(), format='%Y%m%d')
                order_no = RepairOrderManager.gen_repair_order_no(REPAIR_ORDER_NO_PREFIX, timestamp, next_value, seq_max_digits=REPAIR_ORDER_NO_SEQ_DIGITS)
                if not order_no:
                    return False, '生成编号异常'
                repair_order = self.create(
                    order_no=order_no, applicant=applicant, fault_type=fault_type,
                    creator=creator, **kwargs
                )
                seq.seq_value = next_value
                seq.save()
                seq.cache()
                lock.release()
                return True, repair_order
        except Exception as e:
            logger.exception(e)
            return False, '创建报修单异常'

    def dispatch_repair_order(self, repair_order, dispatcher, maintainer, priority, *args, **kwargs):
        """
        分派报修单
        :param repair_order 报修单
        :param dispatcher: 分派人
        :param maintainer: 维修工
        :param priority: 优先级
        :param args:
        :param kwargs: {}
        :return:
        """
        try:
            update_data = dict(
                {
                    "maintainer": maintainer, 'priority': priority, 'status': REPAIR_ORDER_STATUS_DOING,
                    "modifier": dispatcher, 'modified_time': times.now(),
                },
                **kwargs
            )
            repair_order.update(update_data)
            repair_order.cache()
            return repair_order
        except Exception as e:
            logger.exception(e)
            return None

    def handle_repair_order(self, repair_order, operator, result, *args, **kwargs):
        """
        处理报修单
        :param repair_order 报修单
        :param operator: 当前操作人
        :param result: 处理结果
        :param args:
        :param kwargs: {"expenses": expenses, "files": files, "solution": solution, "assert_devices": assert_devices}
        :return:
        """
        try:
            update_data = dict(
                {
                    "result": result, "status": REPAIR_ORDER_STATUS_DONE,
                    "modifier": operator, 'modified_time': times.now()
                },
                **kwargs
            )
            repair_devices = kwargs.get('repair_devices')
            repair_order.update(update_data)
            if repair_devices:
                repair_order.repair_devices.set(repair_devices)
            repair_order.cache()
            return repair_order
        except Exception as e:
            logger.exception(e)
            return None

    def comment_repair_order(self, repair_order, commentator, *args, **kwargs):

        """
        评论此次报修
        :param repair_order: 报修单
        :param commentator: 评论人
        :param args:
        :param kwargs: {"comment_grade": comment_grade, "comment_content": comment_content}
        :return:
        """
        update_data = dict(
            {
                'comment_time': times.now(), "status": REPAIR_ORDER_STATUS_CLOSED,
                'modifier': commentator, 'modified_time': times.now()
            },
            **kwargs
        )
        try:
            repair_order.update(update_data)
            repair_order.cache()
            return repair_order
        except Exception as e:
            logger.exception(e)
            return None

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

    def get_my_create_repair_order(self, staff):
        """
        获取当前登录用户申请/创建的资产设备保修单
        """
        return self.filter(creator=staff)

    def get_repair_order_in_repair(self, staff):
        """
        获取当前登录用户申请的资产设备保修单处于维修中的列表
        """
        return self.filter(maintainer=staff, status=REPAIR_ORDER_STATUS_DOING)

    def get_completed_repair_order(self, staff):
        """
        获取当前登录用户已完成的保修单
        """
        from django.db.models import Q
        query_set = self.filter(
            Q(status=REPAIR_ORDER_STATUS_DONE) | Q(status=REPAIR_ORDER_STATUS_CLOSED)
        ).filter(creator=staff)
        return query_set


class MaintenancePlanManager(BaseManager):

    def create_maintenance_plan(self, storage_places, assert_devices, **data):
        try:
            with transaction.atomic():
                seq = Sequence.objects.select_for_update().get(seq_code=MAINTENANCE_PLAN_NO_SEQ_CODE)
                if not seq:
                    logger.warning('The sequence not exists')
                    return None
                seq.curr_value()
                next_value = seq.next_value()
                timestamp = times.datetime_to_str(times.now(), format='%Y%m%d')
                plan_no = MaintenancePlanManager.gen_maintenance_plan_no(
                    MAINTENANCE_PLAN_NO_PREFIX, timestamp, next_value, seq_max_digits=MAINTENANCE_PLAN_NO_SEQ_DIGITS)
                if not plan_no:
                    return False
                data['plan_no'] = plan_no
                maintenance_plan = self.create(**data)
                maintenance_plan.places.set(storage_places)
                maintenance_plan.assert_devices.set(assert_devices)
                seq.seq_value = next_value
                seq.save()
                seq.cache()
                maintenance_plan.cache()
                return maintenance_plan
        except Exception as e:
            logger.exception(e)
            return None

    @staticmethod
    def gen_maintenance_plan_no(prefix, timestamp, seq, seq_max_digits=2):
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

        maintenance_plan_no = "%s%s%s" % (prefix, timestamp, seq_str)
        return maintenance_plan_no

    def get_maintenance_plan_list(self, search_key=None, status=None, period=None, type=None):
        """
        获取所有设备维护计划列表
        :param search_key: 搜索关键字（设备维护计划编号，设备维护计划名称）
        :param status: 设备状态（NW：未执行，DN：已执行）
        :param period: 时间查询参数（逾期、今天到期、三日内到期、一周内到期、一个月内到期）
        :param type: 资产设备维护计划类型（巡检、保养、盘点）
        """
        from django.db.models import Q
        query_set = self.all()
        if search_key:
            query_set = query_set.filter(
                Q(title__contains=search_key) | Q(plan_no__contains=search_key)
            ).distinct()
        if status:
            query_set = query_set.filter(status=status)
        if type:
            query_set = query_set.filter(type=type)
        if period:
            if period == MAINTENANCE_PLAN_EXPIRED_DATE_BE_OVERDUE:
                query_set = query_set.filter(expired_date__lt=times.get_day_begin_time(times.now()))
            if period == MAINTENANCE_PLAN_EXPIRED_DATE_NOW_DAY:

                query_set = query_set.filter(
                    expired_date__range=(times.get_day_begin_time(times.now()),
                                         times.get_day_end_time(times.now()))
                        )
            if period == MAINTENANCE_PLAN_EXPIRED_DATE_THREE_DAY:

                query_set = query_set.filter(
                    expired_date__range=(
                        times.get_day_begin_time(times.now()),
                        times.get_day_end_time(times.after_days(interval=2)))
                        )
            if period == MAINTENANCE_PLAN_EXPIRED_DATE_ON_WEEK:

                query_set = query_set.filter(
                    expired_date__range=(
                        times.get_day_begin_time(times.now()),
                        times.get_day_end_time(times.after_days(interval=6)))
                )
            if period == MAINTENANCE_PLAN_EXPIRED_DATE_ON_MONTH:

                query_set = query_set.filter(expired_date__range=(
                    times.get_day_begin_time(times.now()),
                    times.get_day_end_time(times.before_days(times.get_next_month(), interval=1))))
        return query_set.order_by('-created_time')


class FaultSolutionManager(BaseManager):

    def create_fault_solution(self, creator, title, fault_type, solution, *args, **kwargs):
        data = dict(
            {
                'creator': creator,
                'title': title,
                'fault_type': fault_type,
                'solution': solution,
                'modified_time': times.now()
            },
            **kwargs
        )
        try:
            return self.create(**data)
        except Exception as e:
            logger.info(e)
            return None

    def bulk_create_fault_solution(self, fs_data, *args, **kwargs):
        if not fs_data:
            return False
        objs = list()
        for data_dict in fs_data:
            objs.append(
                self.model(
                    title=data_dict.get('title'),
                    fault_type=data_dict.get('fault_type'),
                    solution=data_dict.get('solution'),
                    creator=data_dict.get('creator'),
                    modified_time=times.now()
                )
            )
        try:
            self.bulk_create(objs)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def update_fault_solution(self, fault_solution, modifier, title, fault_type, solution, *args, **kwargs):
        data = dict(
            {
                'title': title,
                'fault_type': fault_type,
                'solution': solution,
                'modified_time': times.now(),
                'modifier': modifier
            },
            **kwargs
        )
        try:
            fs = fault_solution.update(data)
            fs.cache()
            return fs
        except Exception as e:
            logger.info(e)
            return None

