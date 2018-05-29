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
    url(r"^login$",        views.OrganLoginView.as_view(), ),  # 未被使用, 推荐/users/login

    # 单个企业get/update/delete
    url(r"^(\d+)$",         views.OrganView.as_view(), name='organs_organ'),

    # 概览页
    url(r'^(\d+)/index$',   views.OrganHomeView.as_view(), ),

    # 企业注册激活
    url(r"^signup_activate$", views.OrganSignupActivationView.as_view(), name='organs_signup_activate'),

    # 单个企业员工 get/put/delete
    url(r"^staffs/(\d+)$", views.StaffView.as_view(), ),

    # 员工信息批量查询,分组员工列表,待邀请列表
    url(r"^(\d+)/staffs$", views.StaffListView.as_view(), ),

    # 创建企业员工post
    url(r"^(\d+)/staffs/create$", views.StaffCreateView.as_view(), ),

    # 权限与权限组
    url(r"^(\d+)/groups$",              views.GroupListView.as_view(), name='organs_group_list'),
    url(r"^(\d+)/groups/create$",       views.GroupCreateView.as_view(), name='organs_group_create'),
    url(r"^(\d+)/groups/permissions$",  views.PermissionListView.as_view(), name='organs_perms'),

    # 返回企业全局数据列表
    url(r"^(\d+)/global_data_list$",    views.OrganGlobalDataListView.as_view(), ),

]