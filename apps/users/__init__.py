# coding=utf-8
#
# Created by junn, on 2016-11-25
#

from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'

default_app_config = 'users.UsersAppConfig'
