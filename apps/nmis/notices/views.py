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
from utils import times

logger = logging.getLogger(__name__)


class NoticeListView(BaseAPIView):
    permission_classes = (HospitalStaffPermission,)

    def get(self, req):
        """
        获取消息列表(筛选调教：已读/未读)
        is_read: false: 未读, true: 已读 None: 全部
        """
        self.check_object_any_permissions(req, None)
        staff = req.user.get_profile()
        is_read = req.GET.get('is_read', '').strip()
        if is_read:
            if is_read not in ('False', 'True'):
                return resp.failed('is_read参数异常')
            query_set = UserNoticeSerializer.setup_eager_loading(
                UserNotice.objects.filter(staff=staff, is_read=is_read, is_delete=False).order_by('-created_time')
            )
        else:
            query_set = UserNoticeSerializer.setup_eager_loading(
                UserNotice.objects.filter(staff=staff, is_delete=False).order_by('-created_time')
            )
        return self.get_pages(query_set, results_name='notices')


class NoticeReadOrDeleteView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @check_params_not_null(['notice_ids', 'op_type'])
    def put(self, req):
        """
        读取消息/删除消息（标记单个/多条消息为删除状态，标记单个/多条消息为已读状态）
        type: 操作类型（删除操作：DE、读取操作:RE）必传字段
        notice_ids: 消息ids集合字符串，如："1,2,3" 必传字段
        """
        staff = req.user.get_profile()
        self.check_object_permissions(req, staff)

        notice_ids = get_id_list(req.data.get('notice_ids', '').strip())

        operation_type = req.data.get('op_type', '').strip()
        if operation_type not in ('RE', 'DE'):
            return resp.failed('不合法的操作类型数据')

        user_notices = UserNotice.objects.filter(notice_id__in=notice_ids, staff=staff)
        if not len(notice_ids) == len(user_notices):
            return resp.failed('检查是否存在不匹配的消息')
        try:
            if operation_type == 'RE':
                if not user_notices.filter(is_read=False):
                    return resp.failed('消息已读，无法改变消息状态')
                user_notices.filter(is_read=False).update(is_read=True, read_time=times.now())
            else:
                # 选中的消息存在未读的情况下未考虑，直接标记成删除状态，如需考虑，后续改进
                user_notices.update(is_delete=True, delete_time=times.now())
            return resp.ok('操作成功')
        except Exception as e:
            logger.exception(e)
            return resp.failed('操作失败')


class NoticeReadOrDeleteAllView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @check_params_not_null(['op_type'])
    def put(self, req):
        """
        op_type: 操作类型（全部标为已读(RE): 所有未读消息标记为已读, 删除全部已读(DE): 所以已读消息标记为删除）
        根据操作类型把消息标记为相对应的状态
        """
        staff = req.user.get_profile()
        self.check_object_permissions(req, staff)

        operation_type = req.data.get('op_type', '').strip()
        if operation_type not in ('ARE', 'ADE'):
            return resp.failed('不合法的操作类型数据')

        try:
            if operation_type == 'ARE':
                query_set = UserNotice.objects.filter(staff=staff, is_read=False)
                if not query_set:
                    return resp.failed('所有消息都标记为已读状态，无法再次标记')
                query_set.update(is_read=True, read_time=times.now())
            else:
                query_set = UserNotice.objects.filter(staff=staff, is_read=True)
                query_set.update(is_delete=True, delete_time=times.now())
            return resp.ok('操作成功')
        except Exception as e:
            logger.info(e)
            return resp.failed('操作失败')

