# coding=utf-8
#
# Created by junn, on 2017/2/27
#

#

from __future__ import absolute_import

import sys
import logging
import base64
import hmac
import urllib
import time
import uuid
import requests
from hashlib import sha1

import settings

logger = logging.getLogger(__name__)


class AliyunAPIAuth(object):
    """
    阿里云API接口鉴权
    """
    def __init__(self, api_base_url):
        self.access_id = settings.ALIYUN_EMAIL.get('access_key_id')
        self.access_secret = settings.ALIYUN_EMAIL.get('access_key_secret')
        self.url = api_base_url

    def sign(self, key_secret, params):
        """ 签名
        :param key_secret:
        :param params:
        :return:
        """
        normal_query_str = ''
        sorted_params = sorted(params.items(), key=lambda params: params[0])
        for (k, v) in sorted_params:
            normal_query_str += '&' + self.percent_encode(k) + '=' + self.percent_encode(v)

        string_to_sign = 'GET&%2F&' + self.percent_encode(normal_query_str[1:])    # 使用get请求方法
        h = hmac.new(key_secret + "&", string_to_sign, sha1)
        return base64.encodestring(h.digest()).strip()

    def percent_encode(self, raw_str):
        encode_str = str(raw_str)
        res = urllib.quote(encode_str.encode('utf-8'), '')
        res = res.replace('+', '%20')
        res = res.replace('*', '%2A')
        return res.replace('%7E', '~')

    def make_url(self, params):
        # 公共请求参数
        full_params = {
            'Format': 'JSON',
            'Version': '2015-11-23',
            'AccessKeyId': self.access_id,
            'SignatureMethod': 'HMAC-SHA1',
            'SignatureVersion': '1.0',
            'SignatureNonce': str(uuid.uuid1()),     # str(uuid.uuid1())
            'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        for key in params.keys():
            full_params[key] = params[key]

        full_params['Signature'] = self.sign(self.access_secret, full_params)
        return self.url + "/?" + urllib.urlencode(full_params)


def send_email(to_email, subject, html_content, text_content=''):
    request_params = {
        'Action':           'SingleSendMail',
        'AccountName':      settings.FROM_EMAIL_ACCOUNT,
        'ReplyToAddress':   'true',     # 为true时, 使用管理控制台中配置的回信地址
        'AddressType':      0,          # 随机账号, 1: 为发信地址
        'ToAddress':        to_email,
        'FromAlias':        settings.FROM_EMAIL_ALIAS,
        'Subject':          subject,
        'HtmlBody':         html_content,
        'TextBody':         text_content  # 同时支持发文本邮件
    }

    api_auth = AliyunAPIAuth(settings.ALIYUN_EMAIL.get('api_base_url'))
    url = api_auth.make_url(request_params)
    return requests.get(url)


if __name__ == '__main__':
    subject = '标题1'
    content = '邮件内容: this is a test email from aliyun'
    response = send_email('xjbean@qq.com', subject, content)
    print(response.text)