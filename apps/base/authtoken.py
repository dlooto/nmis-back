# coding=utf-8
#
# Created by junn, on 2018/5/31
#

# 

import logging
import datetime

from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework import exceptions
from base.exceptions import AuthenticationTokenExpired

from rest_framework.authtoken.models import Token

logs = logging.getLogger(__name__)


class CustomToken(Token):
    """
    !!! Don't put this class into users app, CircularDependencyError would occurred
    自定义Token模型: 代理DRF框架的Token模型, 添加额外的方法和属性
    """
    expired_days = 30    # Token默认超时天数
    expired_minutes = 30

    class Meta:
        proxy = True

    def is_expired(self):
        """ token是否过期 """
        return self.created + datetime.timedelta(days=self.expired_days) < self.created.now()
        # return self.created + datetime.timedelta(minutes=self.expired_minutes) < self.created.now()

    @staticmethod
    def refresh(token):
        assert isinstance(token, Token)
        user = token.user
        token.delete()
        new_token = CustomToken.objects.create(user=user)
        return new_token

    def refresh1(self):  # TODO: 需要测试该方法的可行性...
        """
        用原token刷新获取新的token
        :return:
        """
        new_token = self.objects.create(user=self.user)
        self.delete()
        return new_token


class CustomTokenAuthentication(TokenAuthentication):
    """
    自定义Token认证类
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = CustomToken

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Token

    """
    A custom token model may be used, but must have the following properties.

    * key -- The string identifying the token
    * user -- The user to which the token belongs
    """

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        if token.is_expired():
            raise AuthenticationTokenExpired('Token is expired')
        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword
