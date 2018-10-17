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
]
