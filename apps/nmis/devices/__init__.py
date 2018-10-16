# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 处理资产/设备管理, 报废, 入库, 维修等

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DevicesAppConfig(AppConfig):
    name = 'nmis.devices'
    verbose_name = "设备管理"

default_app_config = 'nmis.devices.DevicesAppConfig'
