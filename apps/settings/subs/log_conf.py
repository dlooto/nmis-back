# coding=utf-8

# Created on 2016-12-02, added by junn


###########################################################
# # LOGGER SYSTEM SETTING, default for product env
###########################################################


import os

# 系统日志参数设置函数
def configure_logging_params(**kwargs):
    return {
        'version': 1,
        'disable_existing_loggers': True,

        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
        },
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] \ '
                          ' [%(levelname)s]- %(message)s'
            },
        },

        'handlers': {
            'sentry': {
                'level': 'WARNING',
                'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(kwargs.get('log_file_root'), kwargs.get('log_file_path')),
                'maxBytes': 1024 * 1024 * 100,  # 100 MB
                'backupCount': 5,
                'formatter': 'standard',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },

        'loggers': {
            'django': {
                'handlers': ['sentry', 'file', 'console'],
                'level': kwargs.get('django_log_level'),
                'propagate': True,
            },
            'django.request': {
                'handlers': ['sentry', 'file', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console', 'file'] if kwargs.get('log_sql_in_file') else ['console'],
                'level': kwargs.get('sql_log_level'),
                'propagate': False,
            },

            'nmis': {
                'handlers': ['sentry', 'file', 'console'],
                'level': kwargs.get('business_log_level'),
            },

        }
    }

LOGGING_SETTINGS = {
    'log_file_root':    os.path.join(os.path.dirname(__file__), '../../logs'),
    'log_file_path':    'nmis-back/server.log',
    'log_sql_in_file':  False,      # 是否将debug级别的SQL语句输出写入日志文件
    'sql_log_level':    'INFO',     # 该设置决定是否输出SQL语句, django框架的SQL语句仅在DEBUG级才能输出. 默认仅输出到console
    'django_log_level': 'DEBUG',    # 该设置决定django框架自身的日志输出
    'business_log_level':'DEBUG',   # 业务模块日志级别
}

LOGGING = configure_logging_params(**LOGGING_SETTINGS)