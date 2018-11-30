from django.apps import AppConfig

import logging

logger = logging.getLogger(__name__)


class NoticeAppConfig(AppConfig):
    name = 'nmis.notices'
    verbose_name = '消息管理'


default_app_config = 'nmis.notices.NoticeAppConfig'

