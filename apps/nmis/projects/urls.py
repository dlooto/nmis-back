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
    path('<int:project_id>/project_milestones/<int:project_milestone_id>/change-milestone',
         views.ProjectPlanChangeMilestoneView.as_view(), ),

    # 为指定项目添加新设备
    path('<int:project_id>/devices/create',      views.ProjectDeviceCreateView.as_view(), ),

    # 项目具体的某个设备get/update/delete操作
    path('<int:project_id>/devices/<int:device_id>',      views.ProjectDeviceView.as_view(), ),

    # 获取项目流程某里程碑下的所有直接子里程碑项
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/children',
        views.ProjectChildMilestonesView.as_view(),
    ),
    # 保存项目中【调研】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/save-research-info',
        views.ProjectMilestoneResearchInfoCreateView.as_view(),
    ),
    # 查看项目中【调研】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/get-research-info',
        views.ProjectMilestoneResearchInfoView.as_view(),
    ),
    # 保存【方案收集】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/save-plan-gather-info',
        views.ProjectMilestonePlanGatheredCreateView.as_view(),
    ),
    # 查看【方案收集】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/get-plan-gather-info',
        views.ProjectMilestonePlanGatheredView.as_view(),
    ),
    # 保存项目中【方案论证】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/save-plan-argument-info',
        views.ProjectMilestonePlanArgumentCreateView.as_view(),
    ),
    # 查看项目中【方案论证】里程碑下的信息
    path(
        '<int:project_id>/project_milestones/<int:project_milestone_id>/get-plan-argument-info',
        views.ProjectMilestonePlanArgumentView.as_view(),
    ),



    # 项目流程接口
    path('flows',               views.ProjectFlowListView.as_view(), ),     # List
    path('flows/create',        views.ProjectFlowCreateView.as_view(), ),   # create
    path('flows/<int:flow_id>', views.ProjectFlowView.as_view(), ),         # get/put/delete

    path('flows/<int:flow_id>/milestones/create',   views.MilestoneCreateView.as_view(), ),   # Create
    path('flows/<int:flow_id>/milestones/<int:mid>', views.MilestoneView.as_view(), ),         # put/delete
    path('flows/<int:flow_id>/milestones/<int:mid>/children', views.FlowChildMilestonesView.as_view(), ),  # put/delete

    # 确定采购方式里程碑(采购方式，文件附件，说明操作)接口
    path('<int:project_id>/project_milestone_states/<int:pro_milestone_states_id>/record-purchase',
         views.MilestoneRecordPurchaseCreateView.as_view(), ),

    # 获取确定采购方式里程碑中所有的信息
    path('<int:project_id>/milestone/<int:milestone_id>/determining-purchase-method',
         views.MilestoneRecordPurchaseView.as_view(),),

    # 启动采购的相关操作接口（保存上传附件，说明）
    path('<int:project_id>/milestone/<int:milestone_id>/save-startup-purchase-info',
         views.MilestoneStartUpPurchaseCreateView.as_view(), ),

    # 获取启动采购中附件和说明信息
    path('<int:project_id>/milestone/<int:milestone_id>/startup-purchase',
         views.MilestoneStartUpPurchaseView.as_view(), ),

    # 合同管理子里程碑保存操作
    path('<int:project_id>/milestone/<int:milestone_id>/purchase-contract',
         views.MilestonePurchaseContractCreateView.as_view(), ),

    # 流程中各里程碑下单个文件上传
    path('<int:project_id>/single-upload-file', views.UploadFileView.as_view(), ),

    # 删除项目里程碑中附件接口
    path('/single-delete-file/<int:doc_id>', views.DeleteFileView.as_view())

]
