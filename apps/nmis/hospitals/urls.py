# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.urls import path

from . import views

logs = logging.getLogger(__name__)


urlpatterns = [
    # 医疗机构注册/登录/验证邮箱/邮箱后缀已存在
    path("signup",       views.HospitalSignupView.as_view(), ),

    # 单个企业get/update/delete
    path("<int:hid>", views.HospitalView.as_view(), ),
    path("<int:hid>/global-data", views.HospitalGlobalDataView.as_view(), ),  # 医院全局初始化数据

    # 医院科室post/update/delete
    path("<int:hid>/departments/<int:dept_id>", views.DepartmentView.as_view(), ),

    path("<int:hid>/departments/create", views.DepartmentCreateView.as_view(), ),  # 创建单个科室

    path("<int:hid>/departments",        views.DepartmentListView.as_view(), ),   # 科室列表操作

    # 批量导科室信息（以上传excel文件的形式）
    path("<int:hid>/departments/batch-upload", views.DepartmentBatchUploadView.as_view(), ),

    # 单个员工查、删、改
    path("<int:hid>/staffs/<int:staff_id>", views.StaffView.as_view(), ),

    # 添加员工、
    path("<int:hid>/staffs/create",     views.StaffCreateView.as_view(), ),

    # # 批量修改员工权限
    # path("<int:hid>/staffs/change-permission",     views.StaffsPermChangeView.as_view(), ),

    # 查询员工列表
    path("<int:hid>/staffs",            views.StaffListView.as_view(), ),

    # 查询员工列表(附带用户角色、角色权限、和部门权限域信息)
    path("<int:hid>/chunk_staffs", views.ChunkStaffListView.as_view(), ),

    # 批量导入员工信息（以上传excel文件的形式）
    path("<int:hid>/staffs/batch-upload", views.StaffBatchUploadView.as_view(), ),

    # # 权限组API列表接口
    # path("<int:hid>/groups",             views.GroupListView.as_view(), ),

    # 创建角色
    path("roles/create", views.RoleCreateView.as_view(), ),

    # 单个角色查、删、改
    path("roles/<int:role_id>", views.RoleView.as_view(), ),

    # 查询角色列表
    path("roles", views.RoleListView.as_view(), ),

    # 获取医院机构下资产设备存储地点列表
    path('<int:hid>/hospital-address', views.HospitalAddressListView.as_view()),

    # 获取用户列表（供下拉菜单使用）
    path('<int:hid>/single-staffs',    views.SingleStaffView.as_view(),),
]
