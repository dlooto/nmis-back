from django.db import models

# Create your models here.
from base.models import BaseModel
from nmis.notices.consts import NOTICE_TYPE_CHOICES, NOTICE_TYPE_REMIND
from nmis.notices.managers import NoticeManager


class Notice(BaseModel):
    """
    消息数据模型
    """
    type = models.CharField('办理方式', max_length=10,
                            choices=NOTICE_TYPE_CHOICES, default=NOTICE_TYPE_REMIND, blank=True)
    content = models.TextField('消息内容', null=True, blank=True)

    objects = NoticeManager()

    class Meta:
        verbose_name = 'A 消息记录'
        verbose_name_plural = 'A 消息记录'
        db_table = 'notices_notice'

    VALID_ATTRS = [
        'type', 'content',
    ]

    def __str__(self):
        return '%s %s' % (self.id, self.content)


class UserNotice(BaseModel):
    """
    用户和相对应消息关系模型
    """

    staff = models.ForeignKey('hospitals.Staff', verbose_name='', blank=True,
                              on_delete=models.PROTECT, related_name='staff_notice')
    notice = models.ForeignKey('Notice', verbose_name='', blank=True,
                               on_delete=models.PROTECT)
    is_read = models.BooleanField('是否已读', default=False)
    is_delete = models.BooleanField('是否已删除', default=False)
    read_time = models.DateTimeField(verbose_name='消息读取时间', null=True)
    delete_time = models.DateTimeField(verbose_name='消息删除时间', null=True)

    class Meta:
        verbose_name = 'A 用户与消息关系'
        verbose_name_plural = 'A 用户与消息关系'
        unique_together = ('staff', 'notice',)
        db_table = 'notices_user_notice'

    VALID_ATTRS = [
        'is_read', 'is_delete', 'read_time', 'delete_time',
    ]

    def __str__(self):
        return '%s' % self.id
