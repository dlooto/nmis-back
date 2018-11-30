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
    path('', views.NoticeListView.as_view(), ),

    # 读取消息/删除消息（标记单个/多条消息为删除状态，标记单个/多条消息为已读状态）
    path('read-or-delete', views.NoticeReadOrDeleteView.as_view(), ),

    # 当前登录用户下的未读消息标记为已读,已读消息标记为删除
    path('read-or-delete-all', views.NoticeReadOrDeleteAllView.as_view(), ),


]
