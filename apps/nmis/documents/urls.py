# coding=utf-8
#
# Created by gong, on 2018-10-16
#

"""

"""

import logging

from django.urls import path

from . import views

logger = logging.getLogger(__name__)

urlpatterns = [
    # 用户上传文件通用接口
    path('upload-file', views.UploadFileView.as_view(), ),

]
