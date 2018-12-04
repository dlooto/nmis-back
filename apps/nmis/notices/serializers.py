# coding=utf-8
#
# Created by zeng, on 2018/11/28
#

# 

import logging
import datetime

from rest_framework import serializers
from base.serializers import BaseModelSerializer
from nmis.notices.models import Notice, UserNotice
from utils import times

logger = logging.getLogger(__name__)


class NoticeSerializer(BaseModelSerializer):

    class Meta:
        model = Notice
        fields = ('id', 'type', 'created_time', 'content')


class UserNoticeSerializer(BaseModelSerializer):
    id = serializers.SerializerMethodField('_get_id')
    created_time = serializers.SerializerMethodField('_get_created_time')
    type = serializers.SerializerMethodField('_get_type')
    content = serializers.SerializerMethodField('_get_content')

    class Meta:
        model = UserNotice
        fields = ('id', 'type', 'created_time', 'content', 'is_read', 'is_delete')

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('notice')
        return queryset

    def _get_id(self, obj):
        return obj.notice.id

    def _get_created_time(self, obj):
        return times.datetime_strftime(d_date=obj.notice.created_time)

    def _get_type(self, obj):
        return obj.notice.type

    def _get_content(self, obj):
        return obj.notice.content

