# coding=utf-8
#
# Created by junn, on 16/11/25
#

import logging
import uuid
import json
from django.urls import reverse

from django.test import TestCase
from django.conf import settings

from utils.eggs import included_in


class TestCaseDataUtils(object):
    BASE_URL = 'http://b.nmis.com'
    FROM_EMAIL_FOR_TEST = 'test@nmis.com'
    EMAIL_PASSWORD = 'xxxx_123456'
    EMAIL_HOST = 'pop.exmail.qq.com'

    def create_user(self, email=None, password=None, active=False):
        from users.models import User
        email = email or 'test_{}@nmis.com'.format(self.get_random_suffix())
        password = password or self.generate_password()
        user = User.objects.create_param_user(
            ('email', email),
            is_active=active,
            password=password
        )
        user.raw_password = password
        return user

    def get_random_suffix(self):
        return str(uuid.uuid4()).split('-')[-1]

    def generate_password(self):
        from users.forms import is_valid_password
        password = self.get_random_suffix()
        if hasattr(self, 'assertTrue'):
            self.assertTrue(is_valid_password(password))
        return password


class BaseTestCase(TestCase, TestCaseDataUtils):
    logger = logging.getLogger('django.test')

    def setUp(self):
        """ 初始化管理员及其他成员 """
        self.user = self.create_user()
        # pass

    def tearDown(self):
        self.user.clear_cache()

    def login(self, user):
        return self.request_login(user.email, user.raw_password)

    def request_login(self, email, password):
        response = self.post(
            reverse('users_login'),
            data={'email': email, 'password': password, "auth_key": "email"}
        )
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Token {}'.format(response.get('authtoken'))
        return response

    def request(self, method, *args, **kwargs):
        """
        :rtype: dict
        """
        response = getattr(self.client, method)(*args, **kwargs)
        return json.loads(response.content)

    ########################################################
    #                       请求方法
    ########################################################
    def get(self, *args, **kwargs):
        return self.request('get', *args, **kwargs)

    def put(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        data = kwargs.get('data')
        if data and isinstance(data, dict):
            kwargs['data'] = json.dumps(data)
        return self.request('put', *args, **kwargs)

    def post(self, *args, **kwargs):
        kwargs['content_type'] = 'application/json'
        data = kwargs.get('data')
        if data and isinstance(data, dict):
            kwargs['data'] = json.dumps(data)
        return self.request('post', *args, **kwargs)

    def raw_post(self, *args, **kwargs):
        """为防止json.dumps出错, 不进行序列化"""
        return self.request('post', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('delete', *args, **kwargs)

    def request_captcha(self):
        """
        :return: (验证码key, 验证码答案)
        """
        from captcha.models import CaptchaStore
        response = self.post(reverse('users_generate_captcha'), data={'-': '-'})
        key = response['data']['captcha_key']
        store = CaptchaStore.objects.filter(hashkey=key).first()
        return key, store.response

    def assert_response_success(self, response):
        """ 断言响应成功, code=10000 """
        return self.assertEqual(response['code'], 10000, msg=response)

    def assert_response_not_success(self, response):
        """ 断言响应不成功, 即code != 10000 """
        return self.assertNotEqual(response['code'], 10000, msg=response)

    def assert_response_failure(self, response):
        """
        断言为失败的响应, code=0
        """
        return self.assertEqual(response['code'], 0, msg=response)

    def assert_response_form_errors(self, response):
        """ 断言表单数据错误 """
        return self.assertEqual(response['code'], 11009, msg=response)

    def assert_response_no_permission(self, response):
        """断言没有权限访问"""
        return self.assertEqual(response['code'], 10600, msg=response)

    def assert_response_exception(self, response):
        with self.assertRaises(AssertionError):
            return self.assert_response_success(response)

    def assert_data_equal(self, expected_data, obj):
        """
        :type expected_data: 期望的数据结果, dict类型
        :type obj: 实际执行的返回结果, Django model object or dict
        """
        if isinstance(obj, dict):
            get = obj.__getitem__
        else:
            get = lambda name: getattr(obj, name)
        for k, v in expected_data.items():
            self.assertEqual(get(k), v)

    def assert_object_in_results(self, data, result_list):
        """
        断言字典数据在指定的数据列表中
        :param data: 字典类型, 期望的结果数据, 如 {"name": "qq"}
        :param result_list: 响应结果数据列表, 每个元素为dict
        """
        for obj in result_list:
            try:
                self.assertDictContainsSubset(data, obj)
                return
            except:
                continue

        raise self.failureException(
            u"数据不在结果列表中: \n data: %s \n result_list: %s" % (data, result_list)
        )

    def assert_object_not_in_results(self, data, result_list):
        """
        断言字典数据不在指定的结果数据列表中
        :param data:
        :param result_list:
        :return:
        """
        with self.assertRaises(AssertionError):
            self.assert_object_in_results(data, result_list)

    def assert_dict_in_results(self, keyword, data, result_dict):
        """
        :param keyword: 需要查看数据的关键字名称
        :param data: 字典类型, 期望的结果数据, 如 {"name": "qq"}
        :param result_dict: 结果数据字典
        :return:
        """
        dict_data = result_dict.get(keyword)
        for k,v in dict_data.items():
            if data == {k: v}:
                logging.info('{}--->{}'.format(k, v))
                return
        raise self.failureException(
            u"数据不在结果列表中\n data: %s \n result_list: %s" % (data, dict_data))
