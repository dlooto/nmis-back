# coding=utf-8
#
# Created by zeng, on 2018-11-28
#

"""

"""

import logging

from django.urls import path

from . import views

logger = logging.getLogger(__name__)
app_name = 'nmis.notices'
# /api/v1/notices/
urlpatterns = [
    # 获取消息列表
    path('',         views.NoticesListView.as_view(), ),


]
