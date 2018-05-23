# coding=utf-8

from base import resp


def check_id(id_key=None):
    """
    检查请求参数中指定key的int类型id值是否有效,
    :param mtd:     装饰的APIView对象内的请求方法(get/post/put/delete等)
    :param id_key:  如 'organ_id', 'position_id'等
    :return:
    """
    def _check(mtd):
        def check(obj, request, *args, **kwargs):
            if id_key:
                id = request.data.get(id_key) or request.GET.get(id_key)
                if not id:
                    return resp.params_err({id_key: u'参数为空'})
                try:
                    int(id)
                except ValueError:
                    return resp.params_err({id_key: u'无效的参数'})
            return mtd(obj, request, *args, **kwargs)
        return check
    return _check


def check_id_list(id_key_list=None):
    """
    检查请求参数中多个int类型参数值是否存在且有效,
    :param mtd:         装饰的APIView对象内的请求方法(get/post/put/delete等)
    :param id_key_list: 如 ['organ_id', 'position_id']等
    :return:
    """
    def _check(mtd):
        def check(obj, request, *args, **kwargs):
            errors = do_param_check(request, id_key_list)
            return resp.params_err(errors) if errors else mtd(obj, request, *args, **kwargs)
        return check
    return _check


def check_not_null(key=None):
    """
    检查请求参数中指定key的参数是否空
    :param mtd:     装饰的APIView对象内的请求方法(get/post/put/delete等)
    :param key:
    :return:
    """
    def _check(mtd):
        def check(obj, request, *args, **kwargs):
            if key:
                value = request.data.get(key) or request.GET.get(key)
                if not value:
                    return resp.params_err({key: u'参数为空'})
            return mtd(obj, request, *args, **kwargs)
        return check
    return _check


def check_params_not_null(key_list=None):
    """
    检查多个参数是否为空
    :param key_list:  参数列表
    :return:
    """
    def _check(mtd):
        def check(obj, request, *args, **kwargs):
            if key_list:
                for key in key_list:
                    value = request.data.get(key) or request.GET.get(key)
                    if not value:
                        return resp.params_err({key: u'参数为空'})
            return mtd(obj, request, *args, **kwargs)
        return check
    return _check


def check_params_not_all_null(key_list=None):
    """
    检查多个参数是否全部为空, 全部为空返回错误, 用于检查可选参数
    @param key_list:
    @return:
    """
    def _check(mtd):
        def check(obj, request, *args, **kwargs):
            if key_list:
                for key in key_list:
                    value = request.data.get(key) or request.GET.get(key)
                    if value:
                        return mtd(obj, request, *args, **kwargs)
                return resp.params_err({','.join(key_list): u'参数为空'})
        return check
    return _check


def check_objects_exist(model_id_dict=None):
    """
    通过要查询的模型对象id列表, 检查模型对象是否存在. 首先检查id值是否有效
    :param key_list:
    """
    def _check_obj(mtd):
        def check(obj, request, *args, **kwargs):
            errors = do_param_check(request, model_id_dict)
            if errors:
                return resp.params_err(errors)

            # TODO: other check...
            return mtd(obj, request, *args, **kwargs)
        return check
    return _check_obj


def do_param_check(request, key_list):
    """ 参数检查 """
    errors = {}
    for key in key_list:
        value = request.data.get(key) or request.GET.get(key)
        if not value:
            errors.update({key: u'参数为空'})
            continue
        try:
            int(value)
        except ValueError:
            errors.update({key: u'无效的参数'})

    return errors









