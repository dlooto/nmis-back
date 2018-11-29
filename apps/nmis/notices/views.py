from django.shortcuts import render

# Create your views here.
import logging

from rest_framework.permissions import AllowAny

from base import resp
from base.views import BaseAPIView
from nmis.notices.models import Notice, UserNotice

logger = logging.getLogger(__name__)


class NoticesListView(BaseAPIView):
    permission_classes = (AllowAny,)

    def get(self, req):
        """
        获取消息列表
        :param req:
        :return:
        """
        staff = req.user.get_profile()
        query_set = Notice.objects.all()

        notice_ids = [str(user_notice.notice.id)
                      for user_notice in UserNotice.objects.filter(staff=staff)]

        return resp.serialize_response(query_set.filter(id__in=notice_ids),
                                       results_name='notices')
