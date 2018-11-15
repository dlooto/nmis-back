# coding=utf-8
#
# Created by junn, on 17/1/7
#

"""

"""

import logging

from base import resp

from base.views import BaseAPIView
from users.permissions import IsSuperAdmin

logger = logging.getLogger(__name__)


class FlushDataView(BaseAPIView):
    permission_classes = [IsSuperAdmin, ]

    def post(self, req):
        return resp.ok('缓存刷新成功')
