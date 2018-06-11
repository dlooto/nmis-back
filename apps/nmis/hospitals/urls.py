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
    path("<hid>",         views.HospitalView.as_view(), ),

    # 医院科室post/update/delete
    path("<hid>/departments/<dept_id>", views.DepartView.as_view(), ),
]
