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

# 文档类型
ARCHIVE = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    '.xltm': 'application/vnd.ms-excel.template.macroEnabled.12',
    '.xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
    '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',

    '.xla': 'application/vnd.ms-excel',
    '.xlc': 'application/vnd.ms-excel',
    '.xlm': 'application/vnd.ms-excel',
    '.xls': 'application/vnd.ms-excel',
    '.xlt': 'application/vnd.ms-excel',
    '.xlw': 'application/vnd.ms-excel',

    '.doc': 'application/msword',
    '.dot': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    '.docm': 'application/vnd.ms-word.template.macroEnabled.12',
    '.wps': 'application/vnd.ms-works',

    '.pot': 'application/vnd.ms-powerpoint',
    '.pps': 'application/vnd.ms-powerpoint',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',

    '.rar': 'application/octet-stream',
    '.zip': 'application/zip',

    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.jpz': 'image/jpeg',
    '.png': 'image/png',
    '.pnz': 'image/png',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.bmp': 'image/bmp',
}

