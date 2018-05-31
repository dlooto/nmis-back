# coding=utf-8

import settings

from base import resp


def debug_allowed(func):
    def _debug_allowed(obj, req, *args, **kwargs):
        if settings.DEBUG:
            return func(obj, req, *args, **kwargs)
        return resp.lean_response('invalid_request_method')
    return _debug_allowed


def login_required(mtd):
    """作用于class-based view请求方法的装饰器"""
    def _login_required(obj, request, *args, **kwargs):
        if request.user.is_authenticated():
            return mtd(obj, request, *args, **kwargs)
        return resp.require_login()
    return _login_required


def login_required_func(func):
    """
    作为method-based view请求函数的装饰器
    """
    def _login_required(request, *args, **kwargs):
        if request.user.is_authenticated():
            return func(request, *args, **kwargs)
        return resp.require_login()
    return _login_required


def sys_admin_required(mtd):
    """
    需要平台管理员超级权限
    :param mtd:  ClassView内定义的请求处理方法名
    :return:  mtd()调用 或 error json response
    """
    def _auth_required(obj, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return resp.require_login()
        if user.is_active and user.is_superuser:
            return mtd(obj, request, *args, **kwargs)
        return resp.permission_denied()

    return _auth_required

def sys_staff_required(mtd):
    """
    需要平台管理员权限
    :param mtd:  ClassView内定义的请求处理方法名
    :return:  mtd()调用 或 error json response
    """
    def _auth_required(obj, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated():
            return resp.require_login()
        if user.is_active and user.is_staff:
            return mtd(obj, request, *args, **kwargs)
        return resp.permission_denied()

    return _auth_required




