#coding=utf-8
#
# Created by junn, on 16/12/4
#

"""

"""

import logging
import requests

from base import resp
from base.views import BaseAPIView
from rest_framework.permissions import AllowAny

from base.decorators import login_required

logs = logging.getLogger(__name__)


class UserView(BaseAPIView):

    @login_required
    def get(self, req):
        req.user.get_authtoken()
        return resp.serialize_response(req.user, results_name='user')


class TestUploadView(BaseAPIView):
    """
    简历上传并解析
    """
    permission_classes = [AllowAny]

    def post(self, req):
        return resp.ok({'count': 0})
