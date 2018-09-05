# coding=utf-8
#
# Created by junn, on 2018-6-7
#

"""

"""

import logging

from django.urls import path

from nmis.projects import views
from nmis.projects.views import ProjectMilestoneResearchInfoCreateView

logs = logging.getLogger(__name__)


# /api/v1/projects/
urlpatterns = [
    # 获取项目总览列表
    path('',         views.ProjectPlanListView.as_view(), ),

    # 获取待分配的项目列表
    path('undispatched', views.ProjectPlanUndispatchedListView.as_view(), ),

    # 已分配项目列表
    path('dispatched', views.ProjectPlanDispatchedListView.as_view(), ),

    # 获取协助的项目列表
    path('assisted', views.ProjectPlanAssistedListView.as_view(), ),

    # 获取我负责的项目列表
    path('performed', views.ProjectPlanPerformedListView.as_view(), ),

    # 获取我申请的项目列表
    path('applied', views.ProjectPlanAppliedListView.as_view(), ),

    # 分配项目协助人员/辅助人员
    path('<int:project_id>/dispatch-assistant', views.ProjectPlanDispatchAssistantView.as_view(), ),

    # 新建项目申请
    path('create',            views.ProjectPlanCreateView.as_view(), ),

    # 单个项目操作 get/update/delete
    path('<int:project_id>',      views.ProjectPlanView.as_view(), ),

    # 分配项目负责人
    path('<int:project_id>/dispatch',       views.ProjectPlanDispatchView.as_view(), ),

    # 重新分配项目负责人
    path('<int:project_id>/redispatch', views.ProjectPlanRedispatchView.as_view(), ),

    # 分配者驳回项目
    path('<int:project_id>/overrule', views.ProjectPlanOverruleView.as_view()),

    # 项目负责人挂起项目
    path('<int:project_id>/pause', views.ProjectPlanPauseView.as_view(), ),

    # 项目负责人取消挂起项目
    path('<int:project_id>/cancel-pause', views.ProjectPlanCancelPauseView.as_view(), ),

    # 责任人启动项目
    path('<int:project_id>/startup',       views.ProjectPlanStartupView.as_view(),),

    # 责任人变更项目里程碑状态
    path('<int:project_id>/change-milestone', views.ProjectPlanChangeMilestoneView.as_view(), ),

    # 责任人变更项目里程碑状态
    path('<int:project_id>/milestones/<int:milestone_id>/finish-milestone',
         views.ProjectPlanFinishMilestoneView.as_view(), ),

    # 为指定项目添加新设备
    path('<int:project_id>/devices/create',      views.ProjectDeviceCreateView.as_view(), ),

    # 项目具体的某个设备get/update/delete操作
    path('<int:project_id>/devices/<int:device_id>',      views.ProjectDeviceView.as_view(), ),

    # 获取项目流程某里程碑节点下的所有直接子里程碑项
    path(
        '<int:project_id>/flow/<int:flow_id>/milestones/<int:milestone_id>/get-children',
        views.ProjectFlowChildMilestones.as_view(),
    ),
    path(
        '<int:project_id>/flow/<int:flow_id>/milestones/<int:milestone_id>/save-research-info',
        ProjectMilestoneResearchInfoCreateView.as_view(),
    ),


    # 项目流程接口
    path('flows',               views.ProjectFlowListView.as_view(), ),     # List
    path('flows/create',        views.ProjectFlowCreateView.as_view(), ),   # create
    path('flows/<int:flow_id>', views.ProjectFlowView.as_view(), ),         # get/put/delete

    path('flows/<int:flow_id>/milestones/create',   views.MilestoneCreateView.as_view(), ),   # Create
    path('flows/<int:flow_id>/milestones/<int:mid>', views.MilestoneView.as_view(), ),         # put/delete


    # 确定采购方式
    path('<int:project_id>/flow/<int:flow_id>/milestone/<int:milestone_id>/record-purchase',
         views.MilestoneRecordPurchase.as_view(), )
]
