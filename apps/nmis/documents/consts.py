# coding=utf-8
#
# Created by gong, on 2018-10-16
#

# 设备模块常量配置

import logging

logger = logging.getLogger(__name__)

# 上传文件基础路径
DOC_UPLOAD_BASE_DIR = 'upload/document/'
DOC_DOWNLOAD_BASE_DIR = 'download/document/'


# 文档类别
FILE_CATE_UNKNOWN = 'UNKNOWN'
FILE_CATE_CHOICES = (
    (FILE_CATE_UNKNOWN, '其他类型/未知类型'),
)

