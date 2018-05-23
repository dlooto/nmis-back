#coding=utf-8
#
# Created on Apr 23, 2014, by Junn
# 
#

import urllib
import httplib
import requests, json
from urlparse import urljoin

from django.utils.functional import cached_property
from django.core.files.uploadedfile import SimpleUploadedFile


class BaseHttpResponse(object):
    """
    基础请求处理后的响应类
    """

    result_data_key = 'data'
    result_error_key = 'error'

    def __init__(self, rsp, exc=None):
        """
        构造器
        :param rsp:     requests.Response object
        :param exc:     exception obj
        """
        self._response = rsp
        self.exc = exc

    def json(self):
        # return json_util.loads(self._response.content)
        return json.loads(self._response.content)

    @cached_property
    def is_failed(self):
        if self.exc is None:
            rsp = self._response
            if isinstance(rsp, requests.Response) and rsp.status_code == 200:
                error = self.exc = self.json().get(self.result_error_key, None)  # 同时设置exc
                return bool(error)
        return True

    @cached_property
    def is_success(self):
        return not self.is_failed

    def get_data(self):
        """
        得到返回的数据

        :rtype: dict
        """
        return self.json()[self.result_data_key]


def request_file(url):
    """
    从远端下载文件, 并构建request.FILES中的uploaded file对象返回.

    :param url:  文件url路径, 如http://abc.im/12345.jpg

    :return:
        SimpleUploadedFile object, it is containned by the request.FILES(dictionary-like object)
    """
    if not url:
        return
    response = requests.get(url)
    return SimpleUploadedFile('file', response.content)


def send_request(host, send_url, protocol='http', method='GET', port=80, params={}, timeout=30,
                 headers={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}):
    """
    发起http或https请求, 并返回结果

    :param:
        send_url = '/api/v2/app/version/541a7131f?token=dF0zeqBMXAP'
        method = 'GET'
        params = {'token': 'dF0zeqAPWs'}
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        host = 'fir.im'
        port = 80

    :return:
        返回响应字符串

    """
    
    encoded_params = urllib.urlencode(params)
    if protocol not in ("http", "https"):
        return None

    if protocol == "http":
        conn = httplib.HTTPConnection(host, port=port, timeout=timeout)
    else:
        port = 443  # 支持https协议(443端口)
        conn = httplib.HTTPSConnection(host, port=port, timeout=timeout)

    conn.request(method, send_url, encoded_params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    
    return response_str
