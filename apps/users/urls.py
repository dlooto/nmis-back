#coding=utf-8
#
# Created by junn, on 16/11/29
#

"""

"""

import logging
import settings

from django.conf.urls import url, include

from users import views

logs = logging.getLogger(__name__)


# /api/v1/users/
urlpatterns = [
    url(r'^$',         views.UserListView.as_view(), ),

    # url(r'^authtoken$',         views.ObtainAuthtokenView.as_view(), ),     # 获取authtoken
    url(r'^verify_token$',      views.VerifyAuthtokenView.as_view(), name='token_verify'),     # 验证authtoken是否有效
    url(r'^refresh_token$',     views.RefreshAuthtokenView.as_view(), name='token_refresh'),    # 过期时刷新authtoken

    url(r'^signup$',            views.SignupView.as_view(), ),         # 一般注册接口
    url(r'^login$',             views.LoginView.as_view(), name='users_login'),          # 一般登录接口
    url(r'^logout$',            views.LogoutView.as_view(), ),         # 退出登录状态

    url(r'^change_password$',   views.PasswordChangeView.as_view(), ),    # 修改密码
    url(r"^check_email_exist$", views.CheckEmailView.as_view(), ),     #及时检查邮箱后缀

    # 用户信息 get/update/delete
    url(r'^(\d+)$',             views.UserView.as_view(), ),

    # 找回密码
    url(r'^request_reset_password$', views.RequestResetPasswordView.as_view(), name='users_request_reset'),  # 发送找回密码邮件
    url(r'^reset_password$',         views.ResetPasswordView.as_view(), name='users_reset_password'),  # 重置密码
    url(r'^verify_key$',             views.VerifyResetRecordKeyView.as_view(), name='users_verify_key'),


]