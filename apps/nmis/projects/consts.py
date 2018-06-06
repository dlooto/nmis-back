# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 项目管理模块组常量配置

import logging

logs = logging.getLogger(__name__)


# 项目申请状态
PRO_STATUS_PENDING = 'PE'
PRO_STATUS_STARTED = 'SD'
PRO_STATUS_DONE = 'DO'

PROJECT_STATUS_CHOICES = (
    (PRO_STATUS_PENDING,    '未开始'),
    (PRO_STATUS_STARTED,    '已启动'),
    (PRO_STATUS_DONE,       '已完成'),
)

