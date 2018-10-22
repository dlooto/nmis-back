#coding=utf-8
#
# Created by junn, on 16/11/29
#

"""

"""

import logging

from django.urls import path

from users import views

logs = logging.getLogger(__name__)


# /api/v1/users/
urlpatterns = [
    path('',         views.UserListView.as_view(), ),

    path('verify-token',      views.VerifyAuthtokenView.as_view(), name='token_verify'),     # 验证authtoken是否有效
    path('refresh-token',     views.RefreshAuthtokenView.as_view(), name='token_refresh'),    # 过期时刷新authtoken

    path('signup',            views.SignupView.as_view(), ),         # 一般注册接口
    path('login',             views.LoginView.as_view(), name='users_login'),          # 一般登录接口
    path('logout',            views.LogoutView.as_view(), ),         # 退出登录状态

    path('change-password',   views.PasswordChangeView.as_view(), ),    # 修改密码
    path("check-email-exist", views.CheckEmailView.as_view(), ),     #及时检查邮箱后缀

    # 用户信息操作 get/update/delete
    path('<user_id>',             views.UserView.as_view(), ),

    # 找回密码
    path('request-reset-password', views.RequestResetPasswordView.as_view(), name='users_request_reset'),  # 发送找回密码邮件
    path('reset-password',         views.ResetPasswordView.as_view(), name='users_reset_password'),  # 重置密码
    path('verify-reset-key',       views.VerifyResetRecordKeyView.as_view(), name='users_verify_key'),

    # 给用户分配角色和权限域
    path('assign-roles-dept-domains/',   views.AssignRolesDeptDomains.as_view(),),
]