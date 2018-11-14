# coding=utf-8
#
# Created by junn, on 2018-5-29
#

# 

import logging

logger = logging.getLogger(__name__)


# 预定义权限组常量
GROUPS = {
    'ADMIN': {
        'name': u'管理员',
        'cate': '',
        'desc': u'* 管理系统所有功能及信息'
    },
    'engineer':   {
        'name': u'工程师',
        'cate': u'',
        'desc': u'派单/维修等'
    }
}