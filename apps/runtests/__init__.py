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

    def create_user(self, email=None, password=None, active=False, **kwargs):
        from users.models import User
        email = email or 'test_{}@nmis.com'.format(self.get_random_suffix())
        password = password or self.generate_password()
        user = User.objects.create_param_user(
            ('email', email),
            is_active=active,
            password=password,
            **kwargs
        )
        user.raw_password = password
        return user

    def create_user_with_username(self, username=None, password=None, active=False, **kwargs):
        username = username or 'test_{}'.format(self.get_random_suffix())
        password = password or self.generate_password()

        from users.models import User
        user = User.objects.create_param_user(
            ('username', username), is_active=active, password=password, **kwargs
        )
        user.raw_password = password
        return user

    def create_organ(self, user, organ_name='测试机构'):
        from nmis.hospitals.models import Hospital
        hospital = Hospital.objects.create(creator=user, auth_status=2, organ_name=organ_name)
        return hospital

    def create_department(self, organ, dept_name='测试科室'):
        return organ.create_department(**{
            'name': dept_name,
            'contact': '13500001111',
            'attri': 'OT',
            'desc': 'test'
        })

    def create_staff(self, user, organ, dept, name=u'测试员工', **kwargs):
        from nmis.hospitals.models import Staff
        return Staff.objects.create(user=user, organ=organ, dept=dept, name=name, **kwargs)

    def create_completed_staff(self, organ, dept, name="员工名字", **kwargs):
        """
        创建staff时同时创建一个user账号, 根据传入的organ和dept参数
        :return:
        """
        user = self.create_user_with_username()
        return self.create_staff(user, organ, dept, name, **kwargs)

    def create_completed_organ(self):
        """
        创建完整的企业数据: 包括企业创建者, 企业对象, 创建者关联的staff对象, 企业权限组等
        :return:
        """
        user = self.create_user_with_username(
            'test_admin123', 'x111111', active=True,
            email='test_{}'.format(self.get_random_suffix())
        )
        organ = self.create_organ(user)
        organ.init_default_groups()
        dept = self.create_department(
            organ, dept_name="测试科室_{}".format(self.get_random_suffix())
        )
        staff = self.create_staff(user, organ, dept=dept)
        staff.set_group(organ.get_admin_group())
        return organ

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

        # 创建机构信息
        self.organ = self.create_completed_organ()

        # 得到机构管理员信息
        self.user = self.organ.creator              # 管理员user账号
        self.admin_staff = self.user.get_profile()  # 管理员staff
        self.dept = self.admin_staff.dept           # 管理员所在科室

    def tearDown(self):
        self.organ.clear_cache()
        self.user.clear_cache()
        self.admin_staff.clear_cache()

    def login(self, user):
        return self.request_login('email', user.email, user.raw_password)

    def login_with_username(self, user):
        return self.request_login('username', user.username, user.raw_password)

    def request_login(self, authkey, authvalue, password):
        response = self.post(
            reverse('users_login'),
            data={authkey: authvalue, 'password': password, "authkey": authkey}
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


