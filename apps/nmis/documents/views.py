# coding=utf-8
#
# Created by gong, on 2018-10-16
#

import logging

from rest_framework.permissions import IsAuthenticated

from base import resp
from base.views import BaseAPIView
from nmis.documents.consts import DOC_UPLOAD_BASE_DIR
from nmis.documents.forms import UploadFileForm

logger = logging.getLogger(__name__)


class UploadFileView(BaseAPIView):

    permission_classes = (IsAuthenticated, )

    def post(self, req):
        """
        文件上传
        :return: 保存至服务器，返回保存路径和原文件名称
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        form = UploadFileForm(req, DOC_UPLOAD_BASE_DIR)
        if not form.is_valid():
            return resp.failed(form.errors)
        result, is_success = form.save()
        if not is_success:
            return resp.failed(msg=result)
        return resp.ok(data={'file': result})
