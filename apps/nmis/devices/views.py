# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from rest_framework.permissions import AllowAny

from base import resp
from base.common.decorators import check_params_not_null
from base.views import BaseAPIView
from nmis.devices.forms import AssertDeviceCreateForm
from nmis.devices.models import AssertDevice, MedicalDeviceSix8Cate
from nmis.hospitals.models import Staff, Department, HospitalAddress

logger = logging.getLogger(__name__)


class AssertDeviceListView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req):
        """
        获取资产设备列表（筛选条件：关键词搜索（设备名称）、设备状态（维修、使用中、报废、闲置））
        """
        # self.check_object_permissions(req, req.user.get_profile().organ)
        querySet = AssertDevice.objects.filter()
        return resp.serialize_response(querySet, results_name='assert_device')


class AssertDeviceCreateView(BaseAPIView):

    permission_classes = (AllowAny, )

    @check_params_not_null(['assert_no', 'title', 'medical_device_cate_id', 'serial_no',
                            'type_spec', 'service_life', 'bar_code', 'production_date',
                            'status', 'storage_place_id', 'purchase_date', 'cate'])
    def post(self, req):
        """
        创建资产设备
        :param req:
        :return:
        """
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
        return resp.ok('ok')
