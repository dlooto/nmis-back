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
PRO_STATUS_OVERRULE = 'OR'
PRO_STATUS_PAUSE = 'PA'

PROJECT_STATUS_CHOICES = (
    (PRO_STATUS_PENDING,    '未开始'),
    (PRO_STATUS_STARTED,    '已启动'),
    (PRO_STATUS_DONE,       '已完成'),
    (PRO_STATUS_OVERRULE,    '已驳回'),
    (PRO_STATUS_PAUSE,       '已挂起'),
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

# 项目类型
PRO_CATE_SOFTWARE = 'SW'
PRO_CATE_HARDWARE = 'HW'

PROJECT_CATE_CHOICES = (
    (PRO_CATE_SOFTWARE,    '信息化项目'),
    (PRO_CATE_HARDWARE,    '医疗器械项目'),
)
