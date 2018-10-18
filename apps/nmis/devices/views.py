# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from rest_framework.permissions import AllowAny
from django.db.models import Q

from base import resp
from base.authtoken import CustomTokenAuthentication
from base.common.decorators import check_params_not_null
from base.views import BaseAPIView
from nmis.devices.consts import ASSERT_DEVICE_STATUS_CHOICES, REPAIR_ORDER_STATUS_CHOICES, \
    REPAIR_ORDER_OPERATION_CHOICES, REPAIR_ORDER_OPERATION_DISPATCH, REPAIR_ORDER_STATUS_DOING, \
    REPAIR_ORDER_OPERATION_HANDLE, REPAIR_ORDER_OPERATION_COMMENT, PRIORITY_CHOICES
from nmis.devices.forms import AssertDeviceCreateForm, AssertDeviceUpdateForm, RepairOrderCreateForm
from nmis.devices.models import AssertDevice, MedicalDeviceSix8Cate, RepairOrder
from nmis.hospitals.models import Staff, Department, HospitalAddress
from nmis.devices.serializers import RepairOrderSerializer
from utils import times

logger = logging.getLogger(__name__)


class AssertDeviceListView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req):
        """
        获取资产设备列表（筛选条件：关键词搜索（设备名称）、设备状态（维修、使用中、报废、闲置））
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        search_key = req.GET.get('search_key')  # 获取参数
        status = req.GET.get('status')
        if status not in dict(ASSERT_DEVICE_STATUS_CHOICES):
            return resp.failed('资产设备状态错误')
        assert_devices = AssertDevice.objects.get_assert_devices(search_key=search_key, status=status)
        self.get_pages(assert_devices, results_name='assert_devices')
        return self.get_pages(assert_devices, results_name='assert_devices')


class AssertDeviceCreateView(BaseAPIView):

    permission_classes = (AllowAny, )

    @check_params_not_null(['assert_no', 'title', 'medical_device_cate_id', 'serial_no',
                            'type_spec', 'service_life', 'production_date',
                            'status', 'storage_place_id', 'purchase_date', 'cate'])
    def post(self, req):
        """
        创建资产设备
        :param req:
        :return:
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        performer = self.get_object_or_404(req.data.get('performer_id'), Staff)
        responsible_dept = self.get_object_or_404(req.data.get('responsible_dept_id'), Department)
        use_dept = self.get_object_or_404(req.data.get('use_dept_id'), Department)
        medical_device_cate = self.get_object_or_404(req.data.get('medical_device_cate_id'), MedicalDeviceSix8Cate)
        storage_place = self.get_object_or_404(req.data.get('storage_place_id'), HospitalAddress)
        creator = req.user.get_profile()
        form = AssertDeviceCreateForm(creator, req.data)
        if not form.is_valid():
            return resp.failed(form.errors)
        assert_device = form.save()
        if not assert_device:
            return resp.failed('操作失败')
        return resp.serialize_response(assert_device, results_name='assert_device')


class MedicalDeviceSix8CateListView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req):
        """
        获取医疗器械类型列表
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        medical_device_six8_cate_list = MedicalDeviceSix8Cate.objects.get_medical_device_six8_cates()

        return resp.serialize_response(
            medical_device_six8_cate_list, results_name='medical_device_six8_cates')


class AssertDeviceView(BaseAPIView):

    permission_classes = (AllowAny, )

    def put(self, req, device_id):
        """
        修改资产设备
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if req.data.get("performer_id"):
            self.get_object_or_404(req.data.get('performer_id'), Staff)
        if req.data.get("use_dept_id"):
            self.get_object_or_404(req.data.get("use_dept_id"), Department)
        if req.data.get('responsible_dept_id'):
            self.get_object_or_404(req.data.get('responsible_dept_id'), Department)
        if req.data.get('medical_device_cate_id'):
            self.get_object_or_404(req.data.get('medical_device_cate_id'), MedicalDeviceSix8Cate)
        if req.data.get('storage_place_id'):
            self.get_object_or_404(req.data.get('storage_place_id'), HospitalAddress)

        modifier = req.user.get_profile()
        form = AssertDeviceUpdateForm(req.data, modifier, assert_device)

        if not form.is_valid():
            return resp.failed(form.errors)
        updated_assert_device = form.save()
        if not updated_assert_device:
            return resp.failed('操作失败')
        return resp.serialize_response(updated_assert_device, results_name='assert_device')

    def get(self, req, device_id):
        """
        资产设备详情
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        assert_device = self.get_object_or_404(device_id, AssertDevice)

        return resp.serialize_response(assert_device, results_name='assert_device')

    def delete(self, req, device_id):
        """
        删除资产设备
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if not assert_device.deleted():
            return resp.failed('操作失败')
        return resp.ok('操作成功')


class AssertDeviceScrapView(BaseAPIView):

    permission_classes = (AllowAny, )

    def put(self, req, device_id):
        """
        资产设备报废处理
        """

        self.check_object_permissions(req, req.user.get_profile().organ)

        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if not assert_device.assert_device_scrapped():
            return resp.failed('操作失败')

        return resp.serialize_response(assert_device, results_name='assert_device')


class RepairOrderCreateView(BaseAPIView):
    """
    提交报修单
    """
    permission_classes = (AllowAny,)

    def post(self, req, ):
        form = RepairOrderCreateForm(req.user.get_profile(), req.data)
        form.is_valid()
        success, repair_order = form.save()
        if not success:
            return resp.failed("操作失败")
        return resp.serialize_response(repair_order, results_name='repair_order',
                                       srl_cls_name='RepairOrderSerializer')


class RepairOrderView(BaseAPIView):

    permission_classes = (AllowAny,)

    def get(self, req, order_id):
        repair_order = self.get_object_or_404(order_id, RepairOrder)
        repair_order_queryset = RepairOrderSerializer.setup_eager_loading(RepairOrder.objects.filter(id=order_id))

        return resp.serialize_response(repair_order_queryset.first(), results_name='repair_order',
                                       srl_cls_name='RepairOrderSerializer')

    def put(self, req, order_id):
        repair_order = self.get_object_or_404(order_id, RepairOrder)
        action = req.data.get('action', '').strip()
        if not action or action not in dict(REPAIR_ORDER_OPERATION_CHOICES):
            return resp.failed('请求数据异常')

        if action == REPAIR_ORDER_OPERATION_DISPATCH:
            priority = req.data.get('priority', '').strip()
            if not priority or priority not in dict(PRIORITY_CHOICES):
                return resp.failed('请求数据异常')
            maintainer_id = req.data.get('maintainer_id')
            maintainer = self.get_object_or_404(maintainer_id, Staff)
            logger.info(req.user.get_profile())
            update_data = {
                'maintainer': maintainer, 'modifier': req.user.get_profile(),
                'modified_time': times.now(), 'status': REPAIR_ORDER_STATUS_DOING, 'priority': priority
            }
            repair_order.update(update_data)
            repair_order.cache()
        if action == REPAIR_ORDER_OPERATION_HANDLE:
            result = req.data.get('result')
            expenses = req.data.get('expenses')
            files = req.data.get('files')
            solution = req.data.get('solution')
            assert_devices = req.data.get('assert_devices')
            update_data = {
                "result": result, "expenses": expenses, "files": files,
                "solution": solution, "assert_devices": assert_devices,
            }


        if action == REPAIR_ORDER_OPERATION_COMMENT:
            pass
        queryset = RepairOrderSerializer.setup_eager_loading(RepairOrder.objects.filter(id=order_id))
        return resp.serialize_response(
            queryset.first(), results_name='repair_order', srl_cls_name='RepairOrderSerializer'
        )



class RepairOrderListView(BaseAPIView):
    authentication_classes = (CustomTokenAuthentication,)

    def get_queryset(self):
        return RepairOrder.objects.all()

    def get(self, req):

        status = req.GET.get('status', '').strip()
        search = req.GET.get('search', '').strip()
        queryset = self.get_queryset()
        if status:
            if status not in dict(REPAIR_ORDER_STATUS_CHOICES):
                return resp.failed("请求数据异常")
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(fault_type__title__contains=search) | Q(order_no__contains=search) |
                Q(creator__name__contains=search)
            )
        return self.get_pages(queryset, srl_cls_name='RepairOrderSerializer', results_name='repair_orders')


class RepairOrderDispatchView(BaseAPIView):

    def put(self):
        pass