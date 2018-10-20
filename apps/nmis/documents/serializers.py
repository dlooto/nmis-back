# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from base.serializers import BaseModelSerializer
from nmis.documents.models import File

logger = logging.getLogger(__name__)


class ProjectDocumentSerializer(BaseModelSerializer):

    class Meta:
        model = File
        fields = (
            'id', 'name', 'cate', "path"
        )

