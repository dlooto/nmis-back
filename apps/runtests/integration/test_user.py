#!/usr/bin/env python
# encoding: utf-8
"""
python manage.py test runtests.test_user
"""

from copy import deepcopy

from django.urls import reverse

from users.forms import is_valid_password

from runtests import BaseTestCase
from base.authtoken import CustomToken
import datetime


class UserTestCase(BaseTestCase):

    login_api = '/api/v1/users/login'

    def test_login(self):
        """
        登录测试
        """
        account = {
            'username': 'abc_test123', 'password': 'x111111',
            'email': 'test_email@nmis.com'
        }
        user = self.create_user_with_username(active=True, **account)
        a_staff = self.create_staff(user, self.organ, self.dept)
        a_staff.set_group(self.organ.get_admin_group())

        data = deepcopy(account)
        data.update({'authkey': 'username'})
        resp = self.post(self.login_api, data=data)

        self.assert_response_success(resp)
        self.assertIsNotNone(resp.get('user'))
        self.assertIsNotNone(resp.get('staff'))
        self.assertIsNotNone(resp.get('authtoken'))

        data.update({'password': 'x222222'})
        resp = self.post(self.login_api, data=data)
        self.assert_response_not_success(resp)

    # def test_verify_key(self):
    #     user = self.create_user(active=True)
    #     record = user.generate_reset_record()
    #
    #     def do_post(key):
    #         return self.post(reverse('users_verify_key'), data={'reset_key': key})
    #
    #     response = do_post('a invalid key')
    #     self.assertEqual(response['code'], 0)
    #
    #     response2 = do_post(record.key)
    #     self.assertEqual(response2['code'], 10000)
    #
    #     record.set_invalid()
    #     response3 = do_post(record.key)
    #     self.assertEqual(response3['code'], 0)
    #
    # def test_activate_user(self):
    #     user = self.create_user(active=False)
    #     self._test_reset_password(user, 'organs_signup_activate', 'activation_key', user_activate_status=True)
    #
    #     self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)  # 登录成功
    #
    # def test_request_reset_password(self):
    #     key, captcha = self.request_captcha()
    #
    #     _do_post = lambda _user: self.post(
    #             reverse('users_request_reset'),
    #             data={'email': _user.email, 'captcha': captcha, 'captcha_key': key, }
    #         )
    #
    #     user = self.create_user(active=True)
    #     response = _do_post(user)
    #     self.assertEqual(response['code'], 10000)
    #
    #     response2 = _do_post(user)
    #     self.assertEqual(response2['code'], 11009)
    #
    # def test_reset_password(self):
    #     self._test_reset_password(self.create_user(active=True), 'users_reset_password', 'reset_key', True)
    #
    #     with self.assertRaises(AssertionError):
    #         self._test_reset_password(self.create_user(active=False), 'users_reset_password', 'reset_key')
    #
    # def test_is_valid_password(self):
    #     expects = [
    #         ('1' * 6, False),
    #         ('a' * 6, False),
    #         ('a' * 10, False),
    #
    #         ('1a' * 3, True),
    #         ('1a' * 10, True),
    #         ('1a' * 10 + '1', False),
    #         ('abc*()123', True),
    #     ]
    #
    #     for password, expected in expects:
    #         self.assertEqual(is_valid_password(password), expected)
    #
    # def _test_reset_password(self, user, viewname, keyname, user_activate_status=None):
    #     reset_record = user.generate_reset_record()
    #     self.assertTrue(reset_record.is_valid())
    #     self.assertEqual(user, reset_record.get_user())
    #     new_password = self.generate_password()
    #     response = self.post(
    #         reverse(viewname),
    #         data={keyname: reset_record.key, 'new_password': new_password},
    #     )
    #     user.refresh_from_db()
    #     reset_record.refresh_from_db()
    #     self.assertTrue(user.check_password(new_password))
    #     self.assertFalse(reset_record.is_valid())
    #
    #     if user_activate_status is not None:
    #         self.assertEqual(user.is_active, user_activate_status)


# class TokenTestCase(BaseTestCase):
#     """
#     用户登录权限Token测试用例
#     """
#
#     def setUp(self):
#         super(self.__class__, self).setUp()
#
#         response = self.login(self.user)
#         self.token = response.get('authtoken')
#
#     def test_refresh(self):
#         """
#         刷新用户Token
#         :return:
#         """
#         url = reverse('token_refresh')
#         token = self.token
#         for i in xrange(3):
#             response = self.post(url, data={'old_token': token})
#             self.assert_response_success(response)
#             self.assertNotEqual(response.get('token'), token)
#             token = response.get('token')
#             self.client.defaults['HTTP_AUTHORIZATION'] = 'Token {}'.format(token)
#         response = self.post(url, data={'old_token': self.token})
#         self.assert_response_failure(response)
#         self.token = token
#
#     def test_verify(self):
#         """
#         验证Token是否有效
#         :return:
#         """
#         url = reverse('token_verify')
#         response = self.post(url, data={'token': self.token})
#         self.assert_response_success(response)
#         self.assertFalse(response.get('is_expired'))
#         response = self.post(url, data={'token': self.token[4:] + self.token[:4]})
#         self.assert_response_failure(response)
#
#         token = CustomToken.objects.get(key=self.token)
#         token.created = token.created - datetime.timedelta(days=token.expired_day)
#         token.save()  # 修改创建时间
#         response = self.post(url, data={'token': self.token})
#         self.assert_response_success(response)
#         self.assertTrue(response.get('is_expired'))
#
#     def test_custom_token(self):
#         """
#         测试Proxy Token对象的可用性
#         :return:
#         """
#         token = CustomToken.objects.get(key=self.token)
#         self.assertFalse(token.is_expired())
#         token.created = token.created - datetime.timedelta(days=token.expired_day)
#         token.save()
#         self.assertTrue(token.is_expired())
#         token.refresh(token)
