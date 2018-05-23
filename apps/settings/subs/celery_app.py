# coding=utf-8


###########################################################
#                   Celery SETTING
###########################################################

from celery import Celery
from kombu import Exchange, Queue


BASE_BROKER_URL = 'redis://:xxxx@nmis.com:6379'

# #####################################################################
#                           Email发送
# #####################################################################

config = {
    'CELERY_TIMEZONE': 'Asia/Shanghai',
    'CELERY_ACCEPT_CONTENT': ['pickle', 'json', 'msgpack', 'yaml'],

    'CELERY_QUEUES': [
        Queue('email_sending_queue', exchange=Exchange('email_sending_queue'), routing_key='email_sending_queue'),
    ],

    'CELERY_ROUTES': {
        'emails.async_send_mail': {'queue': 'email_sending_queue'}
    },
}


EMAIL_CELERY_BROKER_URL = '%s/1' % BASE_BROKER_URL
EMAIL_CELERY_BACKEND_URL = EMAIL_CELERY_BROKER_URL

# 需要为该celery实例启动对应的worker
email_celery_app = Celery(
    'email_celery_app',
    broker=EMAIL_CELERY_BROKER_URL,
    backend=EMAIL_CELERY_BACKEND_URL,
    include=[
        'emails.tasks',
    ]
)
email_celery_app.config_from_object(config)
