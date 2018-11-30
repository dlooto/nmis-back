from django.shortcuts import render

# Create your views here.
import logging

from base import resp
from base.common.decorators import check_params_not_null
from base.common.param_utils import get_id_list
from base.views import BaseAPIView
from nmis.hospitals.permissions import HospitalStaffPermission
from nmis.notices.models import Notice, UserNotice
from nmis.notices.serializers import UserNoticeSerializer

logger = logging.getLogger(__name__)


class NoticeListView(BaseAPIView):
    permission_classes = (HospitalStaffPermission,)

    def get(self, req):
        """
        获取消息列表
        :param req:
        :return:
        """
        self.check_object_any_permissions(req, None)
        staff = req.user.get_profile()
        query_set = UserNoticeSerializer.setup_eager_loading(UserNotice.objects.filter(staff=staff))
        return self.get_pages(query_set, results_name='notices')


class NoticeView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @check_params_not_null(['notice_ids'])
    def delete(self, req):
        """
        删除消息（批量删除/单个删除）
        """
        staff = req.user.get_profile()
        self.check_object_any_permissions(req, staff)
        logger.info(req.user.get_profile())
        notice_ids = get_id_list(req.data.get('notice_ids', '').strip())

        user_notices = UserNotice.objects.filter(notice_id__in=notice_ids, staff=staff)
        if not len(notice_ids) == len(user_notices):
            return resp.failed('检查是否存在不匹配的消息')
        user_notices.update(is_delete=True)
        return resp.ok('操作成功')

