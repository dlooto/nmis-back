# coding=utf-8
#
# Created by junn, on 16/4/15
#

"""

"""

import logging

logs = logging.getLogger(__name__)


class BaseForm():
    """
    Form表单验证基础类. 各子类对该基础类进行重写  :TODO: 待完善...

    自定义form 规范:
        1. 带is_valid()方法, 对数据参数进行验证
        2. 必要时带save方法

    """

    ERR_CODES = {
        'params_error': u'参数错误',
    }

    def __init__(self, data, *args, **kwargs):
        self.data = data
        self.errors = {}

    def update_errors(self, field_name, err_key, *args, **kwargs):
        """
        更新验证错误信息字典
        :param field_name: 返回的错误字典中字段名
        :param err_key: 错误信息key值
        """
        self.errors.update({field_name: self.get_err_msg(err_key, *args, **kwargs)})

    def get_err_msg(self, err_key, *args, **kwargs):
        if not args and not kwargs:
            return self.ERR_CODES.get(err_key)
        return self.ERR_CODES.get(err_key).format(*args, **kwargs)

    def is_valid(self):
        pass

    def save(self):
        pass
