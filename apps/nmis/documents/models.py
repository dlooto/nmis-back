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


class AbstractFile(BaseModel):
    """
    文档模型抽象类
    """
    name = models.CharField('文件真实名称', max_length=128)
    path = models.CharField('文件存放路径', max_length=1024)

    class Meta:
        abstract = True


class File(AbstractFile):
    """
    文件基础模型
    """
    uuid_name = models.CharField('文件在服务器上唯一名称', max_length=128, null=True, blank=True, default='')
    cate = models.CharField(
        '文件类别', max_length=32, default=FILE_CATE_UNKNOWN,
    )
    desc = models.CharField('描述', max_length=255, null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='创建人', on_delete=models.CASCADE)

    objects = FileManager()

    class Meta:
        verbose_name = '文档'
        verbose_name_plural = verbose_name
        db_table = 'documents_file'

    def __str__(self):
        return '%s %s' % (self.id, self.name)






