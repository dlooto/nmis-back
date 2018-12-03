# coding=utf-8
#
# Created by gong, on 2018-10-16
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

    # 医疗器械分类列表
    path('medical-device-cates', views.MedicalDeviceCateListView.as_view(), ),

    # 医疗器械分类列表
    path('medical-device-cate-catalog', views.MedicalDeviceCateCatalogListView.as_view(), ),

    # 医疗器械分类导入
    path('medical-device-cates/import', views.MedicalDeviceCateImportView.as_view(), ),

    # 资产设备详情/修改/删除
    path('<int:device_id>', views.AssertDeviceView.as_view(), ),

    # 资产设备报废处理
    path('<int:device_id>/scrap', views.AssertDeviceScrapView.as_view(), ),

    # 批量导入资产设备
    path('assert_devices/batch-upload', views.AssertDeviceBatchUploadView.as_view(), ),
    # 资产设备调配操作（单个调配、多个调配）
    path('allocate', views.AssertDeviceAllocateView.as_view(), ),

    # 新建设备维护计划单
    path('maintenance_plan/create', views.MaintenancePlanCreateView.as_view(), ),

    # 设备维护计划详情
    path('maintenance_plan/<int:maintenance_plan_id>', views.MaintenancePlanView.as_view(), ),

    # 设备维护计划列表
    path('maintenance_plans', views.MaintenancePlanListView.as_view(), ),

    # 执行资产设备维护计划
    path('maintenance_plan/<int:maintenance_plan_id>/execute', views.MaintenancePlanExecuteView.as_view(), ),

    # 故障类型列表
    path('fault_types', views.FaultTypeListView.as_view()),

    # 提交/新建报修单
    path('repair_orders/create', views.RepairOrderCreateView.as_view(), ),
    # 单个报修单详情/修改/删除/分派/处理/评价
    path('repair_orders/<int:order_id>', views.RepairOrderView.as_view(), ),
    # 报修单列表
    path('repair_orders', views.RepairOrderListView.as_view(), ),
    path('repair_orders/<int:order_id>/repair_order_records', views.RepairOrderRecordListView.as_view(), ),

    # 创建故障/问题解决方案- -知识库
    path('fault_solutions/create', views.FaultSolutionCreateView.as_view()),
    # 单个故障/问题解决方案详情/修改/删除
    path('fault_solutions/<int:fault_solution_id>', views.FaultSolutionView.as_view(), ),
    # 故障/问题解决方案列表--知识库
    path('fault_solutions', views.FaultSolutionListView.as_view(), ),
    # 批量删除故障问题解决方案--知识库
    path('fault_solutions/batch-delete', views.FaultSolutionBatchDeleteView.as_view(), ),
    # 删除故障问题解决方案下的附件-识库知识库
    path('fault_solutions/<int:fault_solution_id>/files/<int:file_id>', views.FaultSolutionFileDeleteView.as_view(), ),

    # 导入故障/问题解决方案列表-知识库
    path('fault_solutions/import', views.FaultSolutionsImportView.as_view(), ),
    # 导出故障/问题解决方案列表-知识库
    path('fault_solutions/export-excel', views.FaultSolutionsExportView.as_view(), ),

    # 医院设备维修统计全局报表
    path('reports/hosp_dev_report', views.OperationMaintenanceReportView.as_view(), ),

]
