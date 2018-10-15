# coding=utf-8
#
# Created by junn, on 2018/5/31
#

# 

import logging
import datetime

from rest_framework.authtoken.models import Token

logs = logging.getLogger(__name__)


class CustomToken(Token):
    """
    !!! Don't put this class into users app, CircularDependencyError would occurred
    自定义Token模型: 代理DRF框架的Token模型, 添加额外的方法和属性
    """
    expired_day = 30    # Token默认超时天数
    expired_seconds = 300

    class Meta:
        proxy = True

    def is_expired(self):
        """ token是否过期 """
        return self.created + datetime.timedelta(days=self.expired_day) < self.created.now()
        # return self.created + datetime.timedelta(days=self.expired_seconds) < self.created.now()

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