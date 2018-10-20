# coding=utf-8
#
# Created by gong, on 2018/10/19
#

# 处理系统相关文档

import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class DocumentsAppConfig(AppConfig):
    name = 'nmis.documents'
    verbose_name = "文档管理"


default_app_config = 'nmis.documents.DocumentsAppConfig'
