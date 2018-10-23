# coding=utf-8


###########################################################
# ##                邮件服务模块
###########################################################

from __future__ import absolute_import

import logging
import requests

import settings
from base.common.param_utils import get_params_after_pop
from emails import aliyun_email

logs = logging.getLogger('django')


class SubMailAPI(object):
    email_service_name = 'submail'

    API_URL = settings.SUBMAIL['api_url']
    APP_ID = settings.SUBMAIL['app_id']
    APP_KEY = settings.SUBMAIL['app_key']

    @classmethod
    def send(cls, email_body):
        params = {
            'appid':        cls.APP_ID,
            'signature':    cls.APP_KEY,
            'from':         email_body.get('from_mail', settings.FROM_EMAIL_ACCOUNT),
            'to':           email_body.get('to_email'),
            'from_name':    email_body.get('from_name', settings.FROM_EMAIL_ALIAS),
            'subject':      email_body.get('subject'),
            'html':         email_body.get('message'),
        }

        logs.debug('Email send params: %s' % get_params_after_pop(params, 'html'))  # 不打印邮件内容
        try:
            response = requests.post(cls.API_URL, data=params)
        except Exception as e:
            logs.exception(e.message)
            return False        # Email发送失败

        return cls._response_success(response)

    @classmethod
    def _response_success(cls, response):
        logs.debug('Email sended result: %s, %s' % (response.status_code, response.json()))
        return (response.status_code == 200) and (response.json().get('status') == 'success')


class AliyunMailAPI(object):
    """
    阿里云邮件发送API
    """

    email_service_name = 'aliyun'
    success_code = (250, 200)  # 阿里定义的请求成功代码

    @classmethod
    def send(cls, email_body):
        logs.debug('Email send params: %s, %s' % (email_body.get('to_email'), email_body.get('subject')))
        try:
            response = aliyun_email.send_email(
                email_body.get('to_email'),
                email_body.get('subject'),
                email_body.get('message'),
            )
        except Exception as e:
            logs.exception(e)
            return False        # Email发送失败

        return cls._response_success(response)

    @classmethod
    def _response_success(cls, response):
        logs.debug('Email send result: %s, %s' % (response.status_code, response.json()))
        return response.status_code in cls.success_code


class MailHelper(object):
    postman = AliyunMailAPI if settings.EMAIL_SERVICE == 'aliyun' else SubMailAPI

    @classmethod
    def send_mail(cls, email_body):  # TODO: 同时给多个email地址发邮件的处理...
        """
        :param email_body: 字典类型, 数据内容如下:
            {
                'from_name':    '流水科技',             # 发件人称呼
                'from_email':   'admin@liushui.com',   # 收件人邮箱
                'to_email':      'hello@abc.com',       # 发件人邮箱
                'subject':      '注册激活',             # 邮件主题
                'message':      '欢迎注册流水科技产品!',  # 邮件内容, 可以为html或者纯文本
                'files':        files,                 # 文件
                'label':        label                  # 标签
            }

        :return: bool, 表示是否发送成功
        """

        return cls.postman.send(email_body)




