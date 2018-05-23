# coding=utf-8
#
# Created by junn, on 16/12/16
#

###########################################################
# ##                短信与邮件设置
###########################################################


# 短信验证码开关, 测试阶段可设为False
SMS_CODE_REQUIRED = True

SMS_CONF = {
    'code_len':     4,          # 短信验证默认长度, 4位数字
    'code_max_limit': 6,        # 同一手机号当天可请求的短信验证码最大条数
    'code_err_limit': 5,        # 同一手机号可允许的验证码最大输入错误次数
    'code_expiry':   10,        # 验证码超时时间, 单位分钟
}

# 用户与账号相关配置
LOGIN_AFTER_SIGNUP = False  # 注册后直接登录

# 邮件配置
FROM_EMAIL_ALIAS = u'NMIS'
CHANGE_NOTIFICATIONS_MIN_INTERVAL = 300     # seconds


# aliyun email setup
ALIYUN_EMAIL = {
    'api_base_url':     "http://dm.aliyuncs.com",
    'access_key_id':    "xxxx",
    'access_key_secret': 'xxxx'
}

FROM_EMAIL_LIST = [  # 发件Email列表, 多个以备用
    'team@nmis.com',
]

MAIL_FUNC_TYPE = 'async'    # 邮件发送类型: async-异步, sync-同步

# 所用的邮件服务
EMAIL_SERVICE = 'aliyun'
FROM_EMAIL_ACCOUNT = FROM_EMAIL_LIST[0] if EMAIL_SERVICE == 'aliyun' else FROM_EMAIL_LIST[1]
