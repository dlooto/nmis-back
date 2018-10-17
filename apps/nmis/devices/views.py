# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

import logging

from django.db.models import Q
from rest_framework.permissions import AllowAny

from base import resp
from base.authtoken import CustomTokenAuthentication
from base.views import BaseAPIView
from nmis.devices.consts import REPAIR_ORDER_STATUS_CHOICES
from nmis.devices.forms import RepairOrderCreateForm
from nmis.devices.models import RepairOrder
from nmis.devices.serializers import RepairOrderSerializer

logger = logging.getLogger(__name__)


class RepairOrderCreateView(BaseAPIView):
    """
    提交报修单
    """
    permission_classes = (AllowAny, )

    def post(self, req, ):
        form = RepairOrderCreateForm(req.user.get_profile(), req.data)
        form.is_valid()
        success, repair_order = form.save()
        if not success:
            return resp.failed("操作失败")
        return resp.serialize_response(repair_order, results_name='repair_order', srl_cls_name='RepairOrderSerializer')


class RepairOrderView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req, order_id):

        repair_order = self.get_object_or_404(order_id, RepairOrder)
        repair_order_queryset = RepairOrderSerializer.setup_eager_loading(RepairOrder.objects.filter(id=order_id))

        return resp.serialize_response(repair_order_queryset.first(), results_name='repair_order', srl_cls_name='RepairOrderSerializer')


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