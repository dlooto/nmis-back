# coding=utf-8
#
# Created by zeng, on 2018/11/28
#

#

import logging

from django.db import transaction

from base.models import BaseManager

from .outofconsumer import send_messages

logger = logging.getLogger(__name__)


class NoticeManager(BaseManager):

    def create_and_send_notice(self, staffs, message):
        """
        生成消息
        :param staffs: 员工集合
        :param message: 推送消息
        """
        try:
            with transaction.atomic():
                notice_data = {'content': message}
                notice = self.create(**notice_data)
                from .models import UserNotice
                user_notice_list = []
                for staff in staffs:
                    user_notice_list.append(
                        UserNotice(staff=staff, notice=notice)
                    )
                UserNotice.objects.bulk_create(user_notice_list)
                send_messages(staffs, message)
                return True
        except Exception as e:
            logger.exception(e)
            return False

    def delete_notice(self):
        """
        删除消息
        :return:
        """
        pass


class UserNoticeManager(BaseManager):

    pass
