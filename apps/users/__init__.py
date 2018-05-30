# coding=utf-8
#
# Created by junn, on 2016-11-25
#

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'


# print('hello==>', settings.AUTH_USER_MODEL)