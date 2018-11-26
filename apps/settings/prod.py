
# coding=utf-8
#
# Created on 2017-2-22
#

############################################################
#                   LOCAL DEV SETTINGS
############################################################


from .base import *


###########################################################
#                      数据库配置
###########################################################

MYSQL_DB = {
    'host': 'localhost',
    'user': 'root',
    'password': 'xxx',
    'port': '3306',
    'conn_max_age': 120,
}

REDIS_DB = {
    'host': 'localhost',  # 缓存使用云Redis
    'port': '6379',
    'user': None,
    'password': 'xxx',

    'cache_db':  '0',
}


DATABASES = {
    "default": {
        "ENGINE":   'django.db.backends.mysql',
        "NAME":     'nmis',
        "USER":     MYSQL_DB['user'],
        "PASSWORD": MYSQL_DB['password'],
        "HOST":     MYSQL_DB['host'],
        "PORT":     MYSQL_DB['port'],
        "CONN_MAX_AGE": MYSQL_DB['conn_max_age'],
        "OPTIONS": {
            'sql_mode': 'STRICT_TRANS_TABLES',
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


MIDDLEWARE += [
    # 'base.middleware.PrintSqlMiddleware',
]

# Sentry settings
RAVEN_CONFIG = {
    'dsn':      'http://xxxx@sentry.nmis.com/15',  # Sentry url
    'release':  'xxx',
}


# 全站对称加密密钥, 请妥善保管
SECRET_KEY = '$^0#lv$Oldiio33dKD8&DF5!kdfDkdf@@@@+//>lkjDFIL__>#**!'


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '120.27.129.147',
    'nmis.com',
    'admin.nmis.com',

]


###########################################################
# 跨域请求白名单, 仅白名单中的域名可跨域请求后端服务
###########################################################

CORS_ORIGIN_WHITELIST = [
    '*.nmis.com',
]

INSTALLED_APPS += ['gunicorn', ]


# 全局本站 URL地址
LOCAL_DOMAIN_URL = 'https://nmis.com/'


###########################################################
#                       日志系统配置
###########################################################

LOGGING_SETTINGS = {
    'log_file_root':    os.path.join(os.path.dirname(__file__), '../../logs'),
    'log_file_path':    'nmis-back/server.log',
    'log_sql_in_file':  False,      # 是否将debug级别的SQL语句输出写入日志文件
    'sql_log_level':    'INFO',     # 该设置决定是否输出SQL语句, django框架的SQL语句仅在DEBUG级才能输出. 默认仅输出到console
    'django_log_level': 'DEBUG',    # 该设置决定django框架自身的日志输出
    'business_log_level':'DEBUG',   # 业务模块日志级别
}

LOGGING = configure_logging_params(**LOGGING_SETTINGS)

