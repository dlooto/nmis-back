# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.conf.urls import url

from . import views

logs = logging.getLogger(__name__)


urlpatterns = [
    # 企业注册/登录/验证邮箱/邮箱后缀已存在
    url(r"^signup$",       views.OrganSignupView.as_view(), ),

    # 单个企业get/update/delete
    url(r"^(\d+)$",         views.OrganView.as_view(), name='organs_organ'),

    # 概览页
    url(r'^(\d+)/index$',   views.OrganHomeView.as_view(), ),

]