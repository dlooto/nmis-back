# coding=utf-8
#
# Created by junn, on 17/1/31
#

# 

import logging, copy

logs = logging.getLogger(__name__)


def get_id_list(str_ids):
    """
    :param str_ids: 字符串形式的id列表, 以逗号分隔, 如 '123,677,976'
    :return: id list
    """
    if not str_ids:
        return []

    try:
        return list(set([id.strip() for id in str_ids.split(',')]))
    except Exception as e:
        logs.debug(e)
        return []


def get_params_after_pop(kwargs, param_key):
    """
    为打印日志等需要, 将字典中的特定参数pop掉
    :param kwargs:
    :param param_key:
    :return:
    """
    if param_key not in kwargs.keys():
        return kwargs
    _kwargs = copy.deepcopy(kwargs)
    _kwargs.pop(param_key)
    return _kwargs