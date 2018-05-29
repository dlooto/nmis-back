#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from base import resp
from base.views import BaseAPIView


logs = logging.getLogger(__name__)


class HospitalHomeView(BaseAPIView):
    """
    机构首页
    """

    def get(self, req, organ_id):
        return resp.ok()








