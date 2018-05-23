# coding=utf-8

import logging
import settings
from settings import email_celery_app
from .email import MailHelper

logger = logging.getLogger('django')


@email_celery_app.task
def async_send_mail(email_body):
    return MailHelper.send_mail(email_body)


def get_mail_func():
    _type = settings.MAIL_FUNC_TYPE.lower()
    if _type == 'sync':
        return MailHelper.send_mail
    elif _type == 'async':
        return async_send_mail.delay
    elif _type == 'debug':
        return lambda *args, **kwargs: logger.info('Send Mail: {} {}'.format(args, kwargs))
    raise TypeError

send_mail_func = get_mail_func()
