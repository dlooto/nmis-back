# coding=utf-8
#
# Created by junn, on 16/11/29
#

# ####################### 响应处理工具类 #############################

import json
import logging

from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from rest_framework.response import Response as RestResponse

from . import codes
from utils.eggs import make_instance

logs = logging.getLogger(__name__)


# ###### 注: 以下必须声明为函数(不可声明为常量), 常量值将只在模块import时被赋值 #########

def ok(msg='', data=None):
    """
    操作成功响应对象. 为成功响应的快捷方式
    :param msg:  响应消息提示, 为空时默认消息内容为 'OK'
    :param data: 为字典类型数据. 该字典数据将append进入{'code': 10000, 'msg': 'OK'}, 并作为
                 response返回
    :return:
            json数据
    """
    if not data:
        data = {}
    if not msg:
        return LeanResponse(codes.append('ok', data))

    result = codes.append('ok', data)
    result['msg'] = msg
    return LeanResponse(result)


def failed(msg='', errors=None):
    """
    操作失败时, 错误消息快捷返回
    :param msg: 错误消息
    :param errors: 错误消息字典, 该字典数据将append进入{'code': 0, 'msg': 'failed'}并返回.
    :return: json数据, like {'code': 0, 'msg': 'Failed'}
    """
    if not errors:
        errors = {}
    if not msg:
        return LeanResponse(codes.append('failed', errors))

    result = codes.append('failed', errors)
    result['msg'] = msg
    return LeanResponse(result)


def require_login():
    return lean_response('login_required')

def permission_denied():
    return lean_response('permission_denied')

def object_not_found():
    return lean_response('object_not_found')

def http404():
    return lean_response('not_found')

def form_err(err_dict):
    """
    post表单错误. 将表单参数验证所有错误项完全返回
    :param err_dict:  所有错误字段, 字典类型
    :return:

    """
    return LeanResponse(codes.append('form_errors', {'errors': err_dict}))


def params_err(err_dict):
    """
    接口请求参数错误
    :param err_dict: 所有错误字段, 字典类型. 如 {"name": u"名字不能为空", "id": u"id不是整数"}
    :return:
    """
    return LeanResponse(codes.append('params_error', {'errors': err_dict}))


def lean_response(crr, msg=''):
    """
    返回简单json响应. 需要添加额外的错误消息时使用该函数
    :param crr: 错误码标识
    :param msg: 可格式化具有占位符的字符串
    """
    if not msg:
        return LeanResponse(codes.get(crr))

    return LeanResponse(codes.format(crr, msg))     # 该处fmat将会拷贝一份常量并修改返回ms值


def string_response(content='', *args, **kwargs):
    """返回普通字符串响应"""
    return HttpResponse(content, *args, **kwargs)


def template_response(request, template, context):
    """
    返回django模板响应
    :param template: django模板
    :param req: request请求对象
    :param context: 返回的字典数据
    """
    return render_to_response(template, RequestContext(request, context))


def redirect_response(url):
    """
    重定向到指定url
    """
    return HttpResponseRedirect(url)


class LeanResponse(HttpResponse):
    """
    简单数据响应.
    仅简单的的json(字典类型)数据直接返回, 使用该响应类型
    """

    def __init__(self, data, status=200, *args, **kwargs):
        """

        :param data: 字典类型数据, 直接作为结果数据返回(不添加其他额外的参数)
        :param status: 响应状态码
        """
        super(LeanResponse, self).__init__(
            json.dumps(data), status=status, *args, **kwargs
        )


SERIALIZABLE_MODULE_NAME = 'serializers'    # 默认序列化模块名
SERIALIZABLE_CLASS_NAME = 'Serializer'      # 默认序列化类名后缀, 如: UserSerializer

def serialize_response(items, results_name='data', app_name=None, srl_cls_name=None):
    """
    返回对象数据(及对象列表数据)json响应. 该函数将数据对象列表转换成相应的Restframework serializer response对象后返回.

    :param items:    数据对象列表. 若数据为QuerySet结果集, 需要先转换成list对象再转入,
                    同时可兼容items为单一数据对象的情况

    :param results_name: 数据结果集名称, 默认为'data'
    :param app_name:    为防止module_name被默认转换成 django.serializers, 传入该参数以确保类类型正确.
    :param srl_cls_name: XxxSerializer类名, 若传入则序列化基于该类进行,
                    否则自动判断数据对象的Serializer类类型. 该参数为字符串类型

    :return:
        Response object, 如下:
            {
              "msg": "ok",
              "code": 10000,
              "data":
              [
                 {
                    "id": 2,
                    "creator":      1  #提醒创建者, 为用户id,
                    "title":        "吃药"  #提醒标题,
                    "spec_date":    "2015-05-04  12:30:00 "  #提醒时间,
                    "repeat_type":  "N"  #重复类型, N-只提醒一次, D-每天提醒,
                    "is_triggered": false  #提醒是否已触发, true-已触发, false-未触发,
                    "is_checked":   false  #提醒是否已查看,
                    "desc":         "这是一个温馨的提醒"
                 },
              ]
            }
    """
    return Response(serialize_data(items, app_name=app_name, srl_cls_name=srl_cls_name), results_name)


def serialize_data(items, app_name=None, srl_cls_name=None):
    """
    返回对象数据(及对象列表数据)的序列化数据结构. 对于单个模型对象及复杂的对象(列表, 或嵌套列表)
    数据均可使用该函数进行转换.

    请确保序列化模块命名与类命名与上方常量规则一致, 即serializers与Serializer.

    :param items:    数据对象列表. 若数据为QuerySet结果集, 需要先转换成list对象再转入,
                    同时可兼容items为单一数据对象的情况

    :param app_name: 为防止module_name被默认转换成 django.serializers, 传入该参数以确保类类型正确.
    :param srl_cls_name: XxxSerializer类名, 若传入则序列化基于该类进行,
                    否则自动判断数据对象的Serializer类类型. 该参数为字符串类型

    :return:
        生成的数据结构如下:
              [     ### 若items为单个对象, 则返回为单一{} 字典结构.
                 {
                    "id": 2,
                    "creator":      1  #提醒创建者, 为用户id,
                    "title":        "吃药"  #提醒标题,
                    "spec_date":    "2015-05-04  12:30:00 "  #提醒时间,
                    "repeat_type":  "N"  #重复类型, N-只提醒一次, D-每天提醒,
                    "is_triggered": false  #提醒是否已触发, true-已触发, false-未触发,
                    "is_checked":   false  #提醒是否已查看,
                    "desc":         "这是一个温馨的提醒"
                 },
              ]
    """
    if not items:
        return []

    if isinstance(items, QuerySet):
        items = list(items)

    if isinstance(items, list):
        instance = items[0]
        many = True
    else:
        instance = items
        many = False

    if app_name:
        module_name = '%s.%s' % (app_name, SERIALIZABLE_MODULE_NAME)  # just like users.serializers
    else:
        # __module__ name such as: nmis.organs.models
        module_str_list = instance.__module__.split('.')
        # 定位models模板或包位置, 解决models模板转换为包产生的问题
        module_str_list = module_str_list[:module_str_list.index('models')]
        module_name = '%s.%s' % ('.'.join(module_str_list), SERIALIZABLE_MODULE_NAME)
        # module_name = '%s.%s' % ('.'.join(instance.__module__.split('.')[:-1]), SERIALIZABLE_MODULE_NAME)

    class_name = '%s%s' % (instance.__class__.__name__, SERIALIZABLE_CLASS_NAME) if not srl_cls_name else srl_cls_name
    logs.debug('make_instance: module_name=%s class_name=%s items=%s' % (module_name, class_name, items))
    return make_instance(module_name, class_name, items, many=many).data


class Response(RestResponse):
    """
    将serializer数据对象构添加数据头(如code/msg)并生成响应对象
    """

    def __init__(self, data, results_name, *args, **kwargs):
        """ 构造响应对象

        :param data: 经过rest-framework框架serializer处理后的数据对象
        :param results_name: 响应数据结果key_name, 如 'data', 'results'等
        """
        super(Response, self).__init__(
            codes.append('ok', {results_name: data}), *args, **kwargs  # 添加固定数据头格式
        )