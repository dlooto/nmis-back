# coding=utf-8
#
# Created by junn, on 2018/5/30
#

# 

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logs = logging.getLogger(__name__)


class CustomizedModelBackend(ModelBackend):
    """
    重写authenticate方法, 使得可以使用phone/email/username任一账号类型登录
    """

    def authenticate(self, password=None, **kwargs):
        user_model = get_user_model()
        auth_key = kwargs.get('auth_key')
        if auth_key not in user_model.VALID_AUTH_FIELDS:
            return None

        try:
            user = user_model._default_manager.get(**{auth_key: kwargs.get(auth_key)})
            if user.check_password(password):
                return user
        except user_model.DoesNotExist:
            return None