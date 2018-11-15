# coding=utf-8
#
# Created by junn, on 17/1/19
#

# 账号与加密处理模块

import logging
import base64

import settings

from utils import des

logger = logging.getLogger(__name__)


def make_password(raw_password, _key=settings.SECRET_KEY):
    """
    使用对称加密算法对原密码进行加密
    :param raw_password:  原密码串
    :param _key: 加密密钥
    :return:  加密后的串
    """
    return base64.b64encode(des.encrypt(raw_password, _key))

def get_raw_password(password, _key=settings.SECRET_KEY):
    """
    返回密码明文
    :param password:  加密后密码
    :param _key:    加密密钥
    :return:
    """
    return des.decrypt(base64.b64decode(password), _key)

