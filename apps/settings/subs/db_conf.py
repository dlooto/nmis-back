# coding=utf-8
#
# Created by junn, on 16/12/27
#

###########################################################
#                      数据库配置
###########################################################

import pymysql

pymysql.install_as_MySQLdb()

MYSQL_DB = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'root',
    'port': '3306',
}

REDIS_DB = {
    'host': '127.0.0.1',
    'port': '6379',
    'user': None,
    'password': 'root',

    'cache_db':  '0',
    'email_db':  '1',
    'spider_db': '10'
}


DATABASES = {
    "default": {
        "ENGINE":   'django.db.backends.mysql',
        "NAME":     'nmis',
        "USER":     MYSQL_DB['user'],
        "PASSWORD": MYSQL_DB['password'],
        "HOST":     MYSQL_DB['host'],
        "PORT":     MYSQL_DB['port'],
        "OPTIONS": {
            'sql_mode': 'traditional', # 'STRICT_TRANS_TABLES',
        },

        # TestCase DB setup
        'TEST': {
            'NAME': 'test_prod_nmis',
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        },
    }
}

# Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:%s@%s:%s/%s' % (
            REDIS_DB['password'], REDIS_DB['host'], REDIS_DB['port'], REDIS_DB['cache_db']
        ),
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            'CONNECTION_POOL_KWARGS': {'max_connections': 1000}
        },
    },
}


