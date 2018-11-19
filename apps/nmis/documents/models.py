# coding=utf-8
#
# Created by gong, on 2018/10/19
#

# 

import logging

from django.db import models

import settings
from base.models import BaseModel
from nmis.documents.consts import FILE_CATE_UNKNOWN
from nmis.documents.managers import FileManager

logger = logging.getLogger(__name__)


class File(BaseModel):
    """
    文件资料模型
    文件存储信息
    """
    name = models.CharField('文件名称', max_length=128)
    path = models.CharField('文件存放路径', max_length=255)
    cate = models.CharField(
        '文件类别', max_length=32, default=FILE_CATE_UNKNOWN,
    )
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='创建人', on_delete=models.CASCADE)

    objects = FileManager()

    class Meta:
        verbose_name = '文件资料'
        verbose_name_plural = verbose_name
        db_table = 'documents_file'
        permissions = (
            ('view_file', 'can view file'),   # 查看文件资料
        )

    VALID_ATTRS = [
        'name', 'path', 'cate',
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)






