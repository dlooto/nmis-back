#coding=utf-8
#
# Created by junn, on 2016-11-25
#

"""

"""

import logging

from django.apps.config import AppConfig

logs = logging.getLogger(__name__)


class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '用户管理'

default_app_config = 'users.UsersConfig'