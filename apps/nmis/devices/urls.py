# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

"""

"""

import logging

from django.urls import path

from . import views

logger = logging.getLogger(__name__)


urlpatterns = [
    # 新建资产设备
    path("create", views.AssertDeviceCreateView.as_view()),

    # 资产设备列表API接口
    path("assert-devices", views.AssertDeviceListView.as_view()),

    # 医疗器械类型列表
    path('medical-device-six8-cates', views.MedicalDeviceSix8CateListView.as_view(), ),

    # 资产设备详情/修改/删除
    path('<int:device_id>', views.AssertDeviceView.as_view(), ),

    # 资产设备报废处理
    path('<int:device_id>/scrap', views.AssertDeviceScrapView.as_view(), ),

    path('repair_orders/create', views.RepairOrderCreateView.as_view(), ),
    path('repair_orders/<int:order_id>', views.RepairOrderView.as_view(), ),
    path('repair_orders', views.RepairOrderListView.as_view(), ),

]
