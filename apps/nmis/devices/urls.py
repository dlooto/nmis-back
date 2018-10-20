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

    # 资产设备调配操作（单个调配、多个调配）
    path('allocate', views.AssertDeviceAllocateView.as_view(), ),

    # 新建设备维护计划单
    path('maintenance_plan/create', views.MaintenancePlanCreateView.as_view(), ),

    # 设备维护详情
    path('maintenance_plan/<int:m_plan_id>', views.MaintenancePlanView.as_view(), ),
    # 故障类型列表
    path('fault_types', views.FaultTypeListView.as_view()),
    # 提交/新建报修单
    path('repair_orders/create', views.RepairOrderCreateView.as_view(), ),
    # 单个报修单详情/修改/删除/分派/处理/评价
    path('repair_orders/<int:order_id>', views.RepairOrderView.as_view(), ),
    # 报修单列表
    path('repair_orders', views.RepairOrderListView.as_view(), ),

]
