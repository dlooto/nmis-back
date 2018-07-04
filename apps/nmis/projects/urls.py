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

    # 分配项目责任人
    path('<int:project_id>/dispatch',       views.ProjectPlanDispatchView.as_view(), ),

    # 责任人启动项目
    path('<int:project_id>/startup',       views.ProjectPlanStartupView.as_view(),),

    # 责任人变更项目里程碑状态
    path('<int:project_id>/change-milestone', views.ProjectPlanChangeMilestoneView.as_view(), ),

    # 为指定项目添加新设备
    path('<int:project_id>/devices/create',      views.ProjectDeviceCreateView.as_view(), ),

    # 项目具体的某个设备get/update/delete操作
    path('<int:project_id>/devices/<int:device_id>',      views.ProjectDeviceView.as_view(), ),

    # # 我的项目列表，带筛选条件
    # path('my-projects',      views.MyProjectListView.as_view()),
    #
    # # 所有待分配项目列表
    # path('allot-projects',   views.AllotProjectListView.as_view()),

    # 项目流程接口
    path('flows',               views.ProjectFlowListView.as_view(), ),     # List
    path('flows/create',        views.ProjectFlowCreateView.as_view(), ),   # create
    path('flows/<int:flow_id>', views.ProjectFlowView.as_view(), ),         # get/put/delete

    path('flows/<int:flow_id>/milestones/create',   views.MilestoneCreateView.as_view(), ),   # Create
    path('flows/<int:flow_id>/milestones/<int:mid>',views.MilestoneView.as_view(), ),         # put/delete

]
