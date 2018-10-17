# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from rest_framework.permissions import AllowAny

from base import resp
from base.common.decorators import check_params_not_null
from base.views import BaseAPIView
from nmis.devices.forms import AssertDeviceCreateForm, AssertDeviceUpdateForm
from nmis.devices.models import AssertDevice, MedicalDeviceSix8Cate
from nmis.hospitals.models import Staff, Department, HospitalAddress

logger = logging.getLogger(__name__)


class AssertDeviceListView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req):
        """
        获取资产设备列表（筛选条件：关键词搜索（设备名称）、设备状态（维修、使用中、报废、闲置））
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        assert_devices = AssertDevice.objects.get_assert_devices()
        return resp.serialize_response(assert_devices, results_name='assert_devices')


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