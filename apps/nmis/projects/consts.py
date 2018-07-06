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

# 项目申请办理方式
PRO_HANDING_TYPE_SELF = 'SE'
PRO_HANDING_TYPE_AGENT = 'AG'

PROJECT_HANDING_TYPE_CHOICES = (
    (PRO_HANDING_TYPE_SELF,     '自行办理'),
    (PRO_HANDING_TYPE_AGENT,    '转交办理'),
)

# 项目流程结束标识
FLOW_DONE = 'DN'
FLOW_UNDONE = 'UN'
FLOW_DONE_SIGN = (
    (FLOW_DONE, '项目流程结束'),
    (FLOW_UNDONE, '项目流程未结束'),
)
