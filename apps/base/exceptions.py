# coding=utf-8
#
# Created by junn, on 17/2/23
#

# 

import logging

from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.exceptions import APIException

from . import codes

logger = logging.getLogger(__name__)


class CsrfError(APIException):
    """
    exception raised when csrf_token incorrect
    """
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'CSRF token missing or incorrect.'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail


code_obj = codes.get('params_error')


class ParamsError(APIException):
    default_code = 'params_error'
    status_code = codes.get(default_code).get('code')
    default_detail = _(codes.get(default_code).get('msg'))


class AuthenticationTokenExpired(APIException):
    """
    exception raised when token expired
    """
    default_code = 'token_expired'
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _(codes.get(default_code).get('msg'))
