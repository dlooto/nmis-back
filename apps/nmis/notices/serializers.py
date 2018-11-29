# coding=utf-8
#
# Created by zeng, on 2018/11/28
#

# 

import logging

from base.serializers import BaseModelSerializer
from nmis.notices.models import Notice

logger = logging.getLogger(__name__)


class NoticeSerializer(BaseModelSerializer):

    class Meta:
        model = Notice
        fields = '__all__'




