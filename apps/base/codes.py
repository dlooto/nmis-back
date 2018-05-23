# coding=utf-8
#
# Created on 2016-12-03, by Junn
#

"""
错误码设置
    code-00403, 前2位为错误码类别, 后3位为错误码. 其中:
"""

CODES = {

    # normal codes
    'ok':           {'code': 10000, 'msg': "OK"},
    'failed':       {'code': 0,     'msg': "Failed"},

    # system err_codes
    'parse_error':              {'code': 10400, 'msg': "malformed request."},   # 请求参数解析错误
    'authentication_failed':    {'code': 10401, 'msg': "incorrect authentication credentials."},
    'csrf_invalid':             {'code': 10403, 'msg': "csrftoken invalid, refresh and set it from the cookies."},
    'not_found':                {'code': 10404, 'msg': "request not found"},
    'method_not_allowed':       {'code': 10405, 'msg': "method not allowed"},
    'not_acceptable':           {'code': 10406, 'msg': "could not satisfy the request's Accept header"},
    'unsupported_media_type':   {'code': 10415, 'msg': "unsupported media type in request."},
    'throttled':                {'code': 10429, 'msg': "request was throttled."},
    'server_error':             {'code': 10500, 'msg': "server error"},

    'not_authenticated':        {'code': 10600, 'msg': "authentication credentials were not provided."},
    'permission_denied':        {'code': 10601, 'msg': "no permission to perform this action."},
    'unauthed_client':          {'code': 10602, 'msg': "Client not authenticated ."},
    'authtoken_error':          {'code': 10603, 'msg': "Error auth_token."},

    'login_required':           {'code': 11001, 'msg': "login required"},
    'account_not_activated':    {'code': 11002, 'msg': "Account not activated"},
    'invalid_page_or_count':    {'code': 11004, 'msg': "invalid page or count"},
    'params_error':             {'code': 11005, 'msg': "parameters input error"},
    'object_not_found':         {'code': 11006, 'msg': "object not found"},
    'operate_duplicated':       {'code': 11008, 'msg': "duplicate operation"},
    'form_errors':              {'code': 11009, 'msg': "form errors"},


    # business code
    #

}


def get(crr):
    """
    返回错误码常量
    :param crr: 错误码常量key值, 如'ok', 'failed'等
    """
    return CODES.get(crr)


def cget(crr):
    """返回错误码常量, 以变量形式重新复制一份"""
    r = CODES.get(crr)
    return r.copy()


def format(crr, msg):
    """ 格式化错误码.
    如  {'code': 10000, 'msg': "failed {0}"} 格式化后将变成
        {'code': 10000, 'msg': "failed 参数错误"}
    """
    if not msg:
        return get(crr)

    result = cget(crr)
    result['msg'] = msg
    return result


def append(crr, _dict):
    """
    在已有错误码内添加新的返回参数.
    如在:
    {'code': 10001, 'msg': "failed"} 里添加 {'data': 'hello'}, 则返回结果为
        {
            'code': 10001,
            'msg': 'failed',
            'data': 'hello'
        }
    """
    result = cget(crr)
    result.update(_dict)
    return result
