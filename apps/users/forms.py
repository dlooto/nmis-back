# coding=utf-8
#
# Created by junn, on 16/12/2
#

"""

"""

import re
import logging

from django.contrib.auth import authenticate, get_user_model

from nmis.hospitals.consts import ARCHIVE
from nmis.projects.consts import DOCUMENT_DIR
from utils import eggs
from base.forms import BaseForm
from users.models import User
from utils.files import upload_file

logger = logging.getLogger(__name__)

PASSWORD_COMPILE = re.compile(r'^(?=.*[a-zA-Z])(?=.*[0-9])')
PASSWORD_ERROR_MSG = u"密码格式不正确"
MOBILE_PHONE_COMPILE = re.compile(r'^1[3458]\d{9}$')


def is_valid_password(password):
    """
    6-20位
    包含数字和字母
    """
    return bool(
        password and (6 <= len(password) <= 20) and PASSWORD_COMPILE.match(password))


class UserSignupForm(BaseForm):
    """用户注册信息验证
    自定义form 规范:
        1. 带is_valid()方法, 对数据参数进行验证
        2. 必要时带save方法
    """

    def __init__(self, req, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.req = req

    def is_valid(self):
        authkey = self.data.get('authkey')  # 取值为 'phone', 'username', or 'email'
        if authkey not in ('phone', 'username', 'email'):
            self.err_msg = u'未知的authkey类型: %s' % authkey
            return False
        if not self.data.get(authkey):
            self.err_msg = u'缺少参数值: %s' % authkey
            return False
        if not getattr(self, 'check_%s' % authkey)():  # 无效则返回
            return False
        if not self.check_password():
            return False

        return True

    def save(self):
        authkey = self.data.get('authkey')
        password = self.data.get('password')
        return User.objects.create_param_user((authkey, self.data.get(authkey)),
                                              password=password, is_active=True)

    def check_username(self):
        username = self.data.get('username')
        if not username:
            self.err_msg = u'无效的用户名'
            return False
        return self._check_auth_name('username')

    def check_phone(self):
        phone = self.data.get('phone')
        if not phone or not eggs.is_phone_valid(phone):
            self.err_msg = u'无效的电话号码'
            return False

        # 如果是手机号注册, 需确保手机号已验证
        phone = phone.strip()
        vcode_key = self.data.get('vcode_key')  # 注册时传入
        if not vcode_key or vcode_key != self.req.session.get('vcode_key_%s' % phone, ''):
            self.err_msg = u'手机号未验证'
            return False

        return self._check_auth_name('phone')

    def check_email(self):
        email = self.data.get('email')
        if not email or not eggs.is_email_valid(email):
            self.err_msg = u'无效的email'
            return False
        return self._check_auth_name('email')

    def check_password(self):
        password = self.data.get('password')
        if not is_valid_password(password):
            self.err_msg = PASSWORD_ERROR_MSG
            return False

        return True

    def _check_auth_name(self, authkey):
        if User.objects.is_exist({authkey: self.data.get(authkey)}):
            self.err_msg = u'%s已被注册' % authkey
            return False
        return True


class UserLoginForm(BaseForm):
    """
    验证用户登录数据.
    """

    ERR_CODES = {
        'params_lack': u'参数缺乏或参数为空',
        'user_not_activated': u'账号未激活',
        'user_not_found': u'账号不存在',
        'user_or_passwd_err': u'用户名或密码错误',
        'no_passwd': u'请输入密码',
        'unknown_auth_key': u'未知的authkey类型'
    }

    def __init__(self, req, data=None, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.req = req
        self.user_cache = None

    def is_valid(self):
        authkey = self.data.get('authkey',
                                '').strip()  # 取值为 'phone', 'username', or 'email'
        if authkey not in ('phone', 'username', 'email'):
            self.update_errors('authkey', 'unknown_auth_key', )
            return False

        auth_value = self.data.get(authkey)
        if not auth_value:
            self.update_errors(authkey, 'params_lack')
            return False

        password = self.data.get('password')
        if not password:
            self.update_errors('password', 'no_passwd')
            return False

        user_model = get_user_model()
        try:
            if authkey == 'username':  # username时需要精确匹配, 区分大小写
                # user = User.objects.get(username__exact=auth_value)  # DB层面大小写无法区分, 所以换用以下语句...
                query_set = user_model.objects.extra(
                    where=["binary username = '%s'" % auth_value])
                if not query_set:
                    self.update_errors(authkey, 'user_not_found')
                    return False
                user = query_set[0]
            else:
                user = user_model.objects.get(**{authkey: auth_value})

            if not user.is_active:
                self.update_errors(authkey, 'user_not_activated')
                return False
            if not user.has_usable_password():
                self.update_errors('password', 'no_passwd')
                return False
        except user_model.DoesNotExist:
            self.update_errors(authkey, 'user_not_found')
            return False
        except Exception as e:
            logger.exception(e)
            self.update_errors(authkey, 'user_not_found')
            return False

        try:
            self.user_cache = authenticate(**{'authkey': authkey, authkey: auth_value,
                                              u'password': password, })  # 传入authkey以标识验证登录类型
        except Exception as e:
            logger.exception(e)
            self.update_errors('password', 'user_or_passwd_err')
            return False

        if not self.user_cache:
            self.update_errors('password', 'user_or_passwd_err')
            return False

        # 如果是被邀请注册用户首次登录, 或者无有效密码(第3方账号登录用户首次用手机号登录)
        if not self.user_cache.is_active:
            self.update_errors('email', 'user_not_activated')
            return False

        return True

    def login(self, req):
        user = self.user_cache
        user.handle_login(req)
        return user


class CheckEmailForm(BaseForm):
    """
    及时验证邮箱后缀是否已注册
    """

    # 以下个人邮箱后缀,可申请试用
    personal_emails = [
        "qq.com",
        "126.com",
        "163.com",
        "gmail.com",
        "hotmail.com",
        "yahoo.com",
        "sina.com",
        "sohu.com",
        "163.net",
        "tom.com",
        "56.com",
        "msn.com",
        "live.com",
        "21cn.com",
        "ask.com",
        "3721.net",
        "yeah.net"
    ]

    def __init__(self, data, *args, **kwargs):
        BaseForm.__init__(self, data, *args, **kwargs)
        self.errors = {}
        self.ERR_CODES.update({
            'invalid_email': u'无效的Email',
            'user_existed': u'Email已注册',
        })

    def is_valid(self):
        return self.check_email_suffix()

    def check_email_suffix(self):
        """
        检查注册Email

        检查项如下:
        1. 格式是否正确
        2. 是否已存在该邮箱账号
        3. 是否有相同后缀的邮箱用户已通过申请
            # 判定是否相同后缀邮箱用户已通过申请
        """

        email = self.data.get('email', '').strip()
        if not email or not eggs.is_email_valid(email):
            self.update_errors('email', 'invalid_email')
            return False
        try:
            get_user_model().objects.get(email=email)
            self.update_errors('email', 'user_existed')
            return False
        except get_user_model().DoesNotExist:
            pass

        email_suffix = email.split('@')[-1]
        if email_suffix in self.personal_emails:
            return True

        if get_user_model().objects.filter(email__contains=email_suffix).exists():
            self.update_errors('email', 'email_existed')
            return False

        return True


class UploadFileForm(BaseForm):

    def __init__(self, req, *args, **kwargs):
        BaseForm.__init__(self, req, *args, **kwargs)
        self.req = req
        self.init_err_codes()

    def init_err_codes(self):
        self.ERR_CODES.update({
            'file_type_err': '不支持的文件类型',
            'file_err': '文件不存在',
            'file_name_err': '文件名称错误',
            'file_size_err': '上传文件过大，默认上传大小2.5M'
        })

    def is_valid(self):
        if not self.check_file_type() or not self.check_file_size() or not self.check_file_key():
            return False
        return True

    def check_file_type(self):
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                if file.content_type not in ARCHIVE.values():
                    self.update_errors('%s' % file.name, 'file_type_err')
                    return False
        return True

    def check_file_name(self):
        pass

    def check_file_key(self):
        if not self.req.FILES.keys():
            self.update_errors('file', 'file_err')
            return False
        return True

    def check_file_size(self):
        """
        校验文件大小，以字节校验，默认2621440字节（2.5M）
        :return:
        """
        for tag in self.req.FILES.keys():
            file = self.req.FILES.get(tag)
            if file.size > 2621440:
                self.update_errors('file_size', 'file_size_err')
                return False
        return True

    def save(self):
        upload_success_files = []
        for tag in self.req.FILES.keys():
            files = self.req.FILES.getlist(tag)
            for file in files:
                result = upload_file(file, DOCUMENT_DIR)
                if result:
                    upload_success_files.append(result)
                else:
                    return '%s%s' % (file.name, '上传失败'), False
        return upload_success_files, True
