# coding=utf-8
#
# Created by junn, on 17/1/7
#

"""
系统缓存管理
"""

import logging
from django_redis import get_redis_connection


logger = logging.getLogger(__name__)

cache_conn = get_redis_connection('default')
if cache_conn:
    cache_conn.flushall()
