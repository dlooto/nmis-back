#!/usr/bin/env python
# encoding: utf-8

import unittest

import settings
from emails import async_send_mail
from emails.email import MailHelper
from runtests import BaseTestCase


class SendEmailTestCase(BaseTestCase):
    def setUp(self):
        self.email_body = {
            'to_email': self.FROM_EMAIL_FOR_TEST,
            'from_email': settings.FROM_EMAIL_ACCOUNT,
            'from_name': settings.FROM_EMAIL_ALIAS,
        }

    def tearDown(self):
        pass

    def test_send_text(self):
        self.email_body.update({'subject': 'text', 'message': u'测试'})
        self.assertTrue(MailHelper.send_mail(self.email_body))

    def test_send_unicode(self):
        self.email_body.update({'subject': 'unicode', 'message': u'测试'})
        self.assertTrue(MailHelper.send_mail(self.email_body))

    def test_send_html(self):
        self.email_body.update({'subject': 'html', 'message': u'<p style="color: green">测试</p>'})
        self.assertTrue(MailHelper.send_mail(self.email_body))

    def test_send_async_mail(self):
        self.email_body.update({
            'subject': u'[async] text',
            'message': u'测试',
        })
        async_send_mail.delay(self.email_body)