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
    path("signup", views.HospitalSignupView.as_view(), ),

    # 单个企业get/update/delete
    path("<hid>", views.HospitalView.as_view(), ),
    # 单个员工查、删、改
    path("<hid>/departments/<dept_id>/staffs/<staff_id>", views.StaffView.as_view(), ),
    # 添加员工、查询员工列表
    path("<hid>/departments/<dept_id>/staffs",views.StaffSignupView.as_view(), ),

]