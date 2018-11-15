# coding=utf-8
#
# Created on 2016-12-02, by Junn
#

###########################################################
#                      短信服务模块
###########################################################


import sys
import logging

import settings
from django.utils import timezone
from django.db import models


from utils import eggs


logger = logging.getLogger(__name__)


# 阿里大鱼短信接口配置
ali_conf = {
    'appkey':   "xxx",
    'secret':   'xxx',
    'domain':   'gw.api.taobao.com',                # 正式环境域名
    'port':     80,
    'resp_key':  'alibaba_aliqin_fc_sms_num_send_response',  # 短信发送接口

    'sign_name':  u"NMIS",
    'sign_name2': u"NMIS",
}

# 阿里短信模板
ali_sms_tpls = {
    'vcode': "xxx",  # 默认为短信验证码模板
}


# def aliyun_send_sms(phone, sms_params, tpl_id, sign_name=ali_conf['sign_name2']):
#     """
#     阿里短信发送接口
#
#     :param phone:      短信要送达的手机号
#     :param sms_params: 短信内容参数, 字典类型, 形如 {'code': 1234}, 具体参数设置由所用短信模板而定
#     :param tpl_id:     短信模板id
#     :param sign_name:  短信签名
#
#     :return:
#         正常发送返回True, 否则返回False及错误消息
#
#     """
#     req = top.api.AlibabaAliqinFcSmsNumSendRequest(domain=ali_conf['domain'], port=ali_conf['port'])
#     req.set_app_info(top.appinfo(ali_conf['appkey'], ali_conf['secret']))
#
#     req.extend = "123456"
#     req.sms_type = "normal"
#
#     req.sms_free_sign_name = sign_name
#     req.sms_template_code = tpl_id
#     req.rec_num = phone
#     req.sms_param = sms_params
#
#     try:
#         resp = req.getResponse()
#         logger.debug(resp)
#         result = resp.get(ali_conf['resp_key'], {}).get('result')
#         if result.get('success'):
#             return True, result.get('msg')
#         return False, result.get('msg')
#     except TopException as e:
#         logger.exception('短信接口请求异常(aliyun_send_sms): \n %s' % e)
#         return False, u'短信接口异常'
#     except Exception as e:
#         logger.exception(e)
#         return False, u'验证码短信发送异常'


# 同一手机号当天可请求的短信验证码最大条数
code_max_limit = settings.SMS_CONF['code_max_limit']


class SmsCodeManager(models.Manager):

    def check_code(self, phone, vcode, expiry=settings.SMS_CONF['code_expiry']):
        """
        检验短信验证码.
        :return: 若验证码有效, 返回True, 否则返回False
        """

        coderecord = self.get_valid_code(phone, vcode, expiry)
        if not coderecord:
            logger.info(u'无效的code: phone %s, code %s' % (phone, vcode))
            return False

        logger.debug('%s' % coderecord)
        coderecord.update(is_valid=False)   # 验证成功后, 置为无效
        return True

    def gen_code(self, phone, tpl_id=ali_sms_tpls['vcode'], re_gen=False,
                 len=settings.SMS_CONF['code_len'], ):
        """
        生成短信验证码并发送到手机号. 默认验证码长度4位

        :param phone: 同一个手机号同一操作(注册/绑定/重置密码其中一种操作)一天之内最多能获取
                    MAX_SMS_LIMIT次验证码.若该手机号码有未使用过的验证码(is_valid=True),
                    则不重新生成新的验证码
        :param re_gen: 当re_gen为True时, 将使该号码之前获取的所有验证码失效, 重新生成.
                       该参数设定可用控制短信发送数目

        :return
        """

        today = timezone.now().date()
        k = self.filter(phone=phone)

        # 若当天该手机号已请求了MAX_SMS_LIMIT次验证码, 则直接返回并警告
        if k.filter(created_time__year=today.year, created_time__month=today.month,
                    created_time__day=today.day, is_valid=False).count() >= code_max_limit:
            logger.warn(u'该手机号(%s)一天之内已获取%s次验证码' % (phone, code_max_limit))
            return False, -1  # 请求验证码次数超过限制

        if re_gen:  # 若要重新生成验证码, 则将之前生成的验证码置为无效状态
            k.filter(is_valid=True).update(is_valid=False)

        # 若存在未过期且有效可用的验证码, 则直接使用而不重新生成. 否则生成新的验证码. 有效期10分钟
        k = k.filter(created_time__gt=timezone.now() - timezone.timedelta(
            minutes=settings.SMS_CONF['code_expiry']), is_valid=True)
        if k and k[0]:
            code = k[0].code
        else:
            code = eggs.random_num(len)
            self.create(phone=phone, code=code)

        if not settings.SMS_CODE_REQUIRED:
            return True, code                   # Just for testing ...

        # success, result = aliyun_send_sms(phone, {'code': code}, tpl_id)
        # if success:
        #     return success, code

        return False, 0     # 验证码短信发送失败

    def get_valid_code(self, phone, vcode, expiry):
        """

        :param phone:  手机号
        :param vcode:  短信验证码
        :param expiry: 超时时间, 单位分钟
        :return:
        """
        return self.filter(phone=phone, code=vcode, is_valid=True,
                           created_time__gt=timezone.now() - timezone.timedelta(
                               minutes=expiry)  # 有效且未超时
                           )


class SmsCode(models.Model):
    """短信验证码记录"""

    phone = models.CharField(u'电话号码', max_length=16)
    code = models.CharField(u'验证码', max_length=16)
    is_valid = models.BooleanField(u'是否可用', default=True)
    created_time = models.DateTimeField(u'创建时间', auto_now_add=True)

    objects = SmsCodeManager()

    def __unicode__(self):
        return "%s, %s" % (self.phone, self.code)

    class Meta:
        db_table = 'users_smscode'
        verbose_name = u'短信验证码'
        verbose_name_plural = u'短信验证码'

    def is_expired(self):
        """是否已过期"""
        delta = timezone.now() - self.created_time
        return delta.seconds > settings.SMS_CODE_EXPIRY * 60