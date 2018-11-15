# coding=utf-8
#
# Created by junn, on 2018/6/13
#

# 

import logging

from nmis.hospitals.models import Staff
from runtests import BaseTestCase

logger = logging.getLogger(__name__)


class StaffCreateTestCase(BaseTestCase):

    def test_staff_create(self):
        """
        测试员工创建的manager方法
        :return:
        """
        user_data = {
            'username': 'staff_name_%s' % self.get_random_suffix(),
            'password': '111111'
        }
        data = {
            "name": "员工名1",
            "title": "主任医师",
            "contact": "15980009999",
            "email": "test@qq.com",
        }
        staff = Staff.objects.create_staff(self.organ, self.dept, user_data, **data)
        self.assertIsNotNone(staff)
        self.assertIsNotNone(staff.user)
        self.assertEquals(staff.user.username, user_data.get('username'))
        self.assertEquals(staff.name, data.get('name'))