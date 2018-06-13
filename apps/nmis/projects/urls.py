# coding=utf-8
#
# Created by junn, on 2018-6-7
#

"""

"""

import logging

from django.urls import path

from nmis.projects import views

logs = logging.getLogger(__name__)


# /api/v1/projects/
urlpatterns = [
    path('',         views.ProjectPlanListView.as_view(), ),

    # 新建项目申请
    path('create',            views.ProjectPlanCreateView.as_view(), ),

    # 单个项目操作 get/update/delete
    path('<int:project_id>',      views.ProjectPlanView.as_view(), ),

    # 为指定项目添加新设备
    path('<int:project_id>/devices/create',      views.ProjectDeviceCreateView.as_view(), ),

    # 项目具体的某个设备get/update/delete操作
    path('<int:project_id>/devices/<int:device_id>',      views.ProjectDeviceView.as_view(), ),


]