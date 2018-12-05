# coding=utf-8
#
# Created by zeng, on 2018/10/29
#

#

import logging

from nmis.notices.models import UserNotice
from runtests import BaseTestCase
from runtests.common.mixins import NoticeMixin


logger = logging.getLogger(__name__)


class NoticeApiTestCase(BaseTestCase, NoticeMixin):

    def test_notices(self):
        """
        API测试: 消息列表API接口测试
        """
        api = "/api/v1/notices/"

        self.login_with_username(self.user)
        # 创建当前登录员工的消息、消息与员工对应关系
        for i in range(0, 5):
            is_success = self.create_notice(staff=self.admin_staff)
            self.assertTrue(is_success)
        response = self.get(api)
        self.assert_response_success(response)
        notices = response.get('notices')
        self.assertIsNotNone(notices)
        self.assertEquals(len(notices), 5)
        # 测试获取已读/未读消息列表（is_read：True代表已读，False代表未读）
        res = self.get(api, data={
            'is_read': True
        })
        self.assert_response_success(res)
        self.assertIsNotNone(res)
        self.assertEquals(len(res.get('notices')), 0)

    def test_read_or_del_notices(self):
        """
        API测试: 读取消息/删除消息（标记单个/多条消息为删除状态，标记单个/多条消息为已读状态）API接口测试
        """
        api = "/api/v1/notices/read-or-delete"
        self.login_with_username(self.user)

        for i in range(0, 5):
            is_success = self.create_notice(staff=self.admin_staff)
            self.assertTrue(is_success)
        u_notices = self.get_notices(staff=self.admin_staff)
        self.assertEquals(len(u_notices), 5)
        notice_ids = ','.join([str(u_notice.notice.id) for u_notice in u_notices])
        self.assertIsNotNone(notice_ids)
        # 读取消息
        res = self.put(api, data={
            'notice_ids': notice_ids,
            'op_type': 'RE'
        })
        self.assert_response_success(res)
        new_u_notices = self.get_notices(staff=self.admin_staff)
        for new_u_notice in new_u_notices:
            self.assertEquals(new_u_notice.is_read, True)
        # 删除消息
        res = self.put(api, data={
            'notice_ids': notice_ids,
            'op_type': 'DE'
        })
        self.assert_response_success(res)
        new_u_notices = self.get_notices(staff=self.admin_staff)
        for new_u_notice in new_u_notices:
            self.assertEquals(new_u_notice.is_delete, True)

    def test_read_or_delete_all_notices(self):
        """
        API测试: 读取所有未读消息/删除所有已读消息API接口测试
        """
        api = '/api/v1/notices/read-or-delete-all'
        self.login_with_username(self.user)

        for i in range(0, 5):
            is_success = self.create_notice(staff=self.admin_staff)
            self.assertTrue(is_success)
        # 读取所有未读的消息
        res = self.put(api, data={
            'op_type': 'ARE'
        })
        self.assert_response_success(res)
        self.assertEquals(res.get('code'), 10000)
        user_notices = UserNotice.objects.all()
        for user_notice in user_notices:
            self.assertEquals(user_notice.is_read, True)
        # 删除所有已读消息
        res = self.put(api, data={
            'op_type': 'ADE'
        })
        self.assert_response_success(res)
        self.assertEquals(res.get('code'), 10000)
        user_notices = UserNotice.objects.filter(is_read=True)
        for user_notice in user_notices:
            self.assertEquals(user_notice.is_delete, True)