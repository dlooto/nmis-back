# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 采购流程: 采购申请, 审批, 采购计划, 合同管理等

import logging

from django.apps import AppConfig

logs = logging.getLogger(__name__)


class ProjectsAppConfig(AppConfig):
    name = 'nmis.projects'
    verbose_name = "项目管理"

default_app_config = 'nmis.projects.ProjectsAppConfig'
