# 项目申请状态
NOTICE_TYPE_ANNOUNCE = 'AN'
NOTICE_TYPE_REMIND = 'RE'
NOTICE_TYPE_MESSAGE = 'ME'


NOTICE_TYPE_CHOICES = (
    (NOTICE_TYPE_ANNOUNCE,      '公告类消息'),
    (NOTICE_TYPE_REMIND,        '提醒类消息'),
    (NOTICE_TYPE_MESSAGE,       '系统类消息')
)