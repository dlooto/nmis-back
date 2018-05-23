# coding=utf-8
#
# Created by junn, on 16/11/29
#

"""
Users view
"""

import logging

from django.contrib.auth import logout as system_logout

from rest_framework.permissions import AllowAny

from base import resp
from base import codes
from base.resp import LeanResponse
from base.views import BaseAPIView

import settings
from utils.eggs import get_email_host_url
from emails.tasks import send_reset_password_mail
from users.forms import UserSignupForm, UserLoginForm, CheckEmailForm
from users.models import User, ResetRecord
from users.models import CustomToken
from nmis.common.decorators import check_not_null

logs = logging.getLogger(__name__)


class ObtainAuthtokenView(BaseAPIView):
    """
    获取authtoken
    """

    def post(self, req):
        pass


class RefreshAuthtokenView(BaseAPIView):
    """
    使用旧的authtoken刷新authtoken.
    """

    @check_not_null('old_token')
    def post(self, req):
        old_token = req.data.get('old_token')
        tokens = CustomToken.objects.filter(key=old_token)
        if not tokens:
            return resp.failed('操作失败')

        new_token = CustomToken.refresh(tokens.first())
        return resp.ok('操作成功', {'token': new_token.key})


class VerifyAuthtokenView(BaseAPIView):
    """
    验证authtoken. 判断是否有效: token合法性, 是否过期(根据created属性)
    """

    permission_classes = (AllowAny,)

    @check_not_null('token')
    def post(self, req):
        token = req.data.get('token')
        tokens = CustomToken.objects.filter(key=token)
        if not tokens:
            return resp.failed('操作失败')
        return resp.ok('操作成功', {'is_expired': tokens.first().is_expired()})


class SignupView(BaseAPIView):
    """ 注册. 暂未被使用 """

    permission_classes = (AllowAny, )
    LOGIN_AFTER_SIGNUP = True  # 默认注册后自动登录

    def post(self, req):
        form = UserSignupForm(req, data=req.POST)
        if form.is_valid():
            user = form.save()

            if not self.LOGIN_AFTER_SIGNUP:
                return resp.ok()

            user.handle_login(req)
            # 注册并登录后, 仅返回uid
            response = resp.ok({'uid': user.id})
            token = user.get_authtoken()
            if not token:
                return resp.lean_response('authtoken_error')
            response.set_cookie('authtoken', token)
            return response

        return resp.failed(form.err_msg)


class LoginView(BaseAPIView):
    """
    该接口为统一登录接口, 无论用户何种身份都可使用该接口登录, 不同身份将后续将跳转到不同页面.
    支持phone/username/email等不同账号类型登录系统.
    """

    permission_classes = (AllowAny, )

    def post(self, req):
        form = UserLoginForm(req, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)

        user = form.login(req)
        response = resp.serialize_response(user, results_name='user')
        return append_extra_info(user, req, response)


class PasswordChangeView(BaseAPIView):
    """ 登录用户修改密码 """

    def post(self,req):
        old_passwod = req.data.get('old_password', '')
        new_password = req.data.get('new_password', '')
        confirm_password = req.data.get('confirm_password', '')

        user = req.user
        if new_password != confirm_password:
            return resp.failed(u'两次密码不一致')

        if not user.check_password(old_passwod):
            return resp.failed(u'密码错误')

        user.set_password(confirm_password)
        user.save()
        return resp.ok(u'密码修改成功')


class UserListView(BaseAPIView):

    def get(self, req):
        return resp.serialize_response(list(User.objects.all()))


class UserView(BaseAPIView):
    def get(self, req, user_id):
        try:
            user = User.objects.get(id=int(user_id))
            return resp.serialize_response(user)
        except User.DoesNotExist:
            return resp.object_not_found()


class LogoutView(BaseAPIView):
    """ 退出 """

    def post(self, req):
        if not req.user.is_authenticated():
            return resp.failed(u'非登录状态')

        system_logout(req)
        return resp.ok()


class RequestResetPasswordView(BaseAPIView):
    """申请找回密码"""

    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        captcha = request.data.get('captcha')
        captcha_key = request.data.get('captcha_key')
        errors = {}

        if email:
            user = User.objects.filter(email=email).first()
            if user:
                reset_record = user.generate_reset_record()
                send_reset_password_mail(
                    user=user, key=reset_record.key,
                    # base_url=request.build_absolute_uri('/'),
                    base_url=settings.LOCAL_DOMAIN_URL
                )
                return resp.ok(data={'data': {'email_host_url': get_email_host_url(email)}})
        errors['email'] = '邮箱不存在'
        return resp.form_err(errors)


class ResetPasswordView(BaseAPIView):
    """重置密码"""

    permission_classes = (AllowAny, )

    def post(self, request):
        reset_key_keyname = 'reset_key'
        new_password_keyname = 'new_password'

        reset_key = request.data.get(reset_key_keyname)
        new_password = request.data.get(new_password_keyname)

        response = User.objects.reset_password(
            new_password=new_password,
            new_password_keyname=new_password_keyname,
            reset_key=reset_key,
            reset_key_keyname=reset_key_keyname,
            activate_user=False,
            activate_require=True,
            login_user=True,
            request=request,
        )

        return response


class VerifyResetRecordKeyView(BaseAPIView):
    """
    检测ResetRecord是否有效
    """

    permission_classes = (AllowAny, )

    def _fail(self, data):
        ret = codes.format('failed', '')
        ret.update(data)
        return LeanResponse(ret)

    def fail(self, **kwargs):
        return self._fail(kwargs)

    def get_value_and_name(self, request):
        for name in ('reset_key', 'activation_key'):
            value = request.data.get(name)
            if value:
                return value, name
        return ()

    def post(self, request):
        value_name = self.get_value_and_name(request)
        if not value_name:
            return resp.failed(u'参数不正确')

        # 参数正确
        value, name = value_name
        logs.info('verify {}: {}'.format(name, value))

        record = ResetRecord.objects.filter(key=value).first()
        if record:
            if record.is_valid():
                return resp.ok()
            if record.expired():
                return self.fail(status='expired', msg=u'链接已过期')
            if record.used():
                return self.fail(status='used', msg=u'链接已被使用')

        # 没有相关key的记录
        return self.fail(status='invalid', msg=u'链接不合法')


class CheckEmailView(BaseAPIView):
    """
    及时检查邮箱后缀存在
    """
    permission_classes = (AllowAny,)

    def post(self, req):
        form = CheckEmailForm(data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        return resp.ok('ok')


def append_extra_info(user, request, response):  # TODO: 后续考虑重构该方法, 提取到view
    """
    用户登录成功后在 ``Response`` 中添加token, profile等其它数据

    :return: Response
    """

    token = user.get_authtoken()
    if not token:
        return resp.lean_response('authtoken_error')
    response.data.update({'authtoken': token})

    # 获取用户profile
    profile = user.get_profile()
    if not profile:
        return resp.failed(u'账号不存在，有问题请联系企业管理员')
    response.data.update({'staff': resp.serialize_data(profile)})

    if profile and hasattr(profile, 'organ'):
        # 返回organ_id, 临时处理方式(后续重构). organ相关逻辑已侵入user模块
        response.data.update({'attach_id': profile.organ_id})
    else:
        response.data.update({'attach_id': ''})

    # 设置登录成功后的跳转页面, 默认到index页
    response.data.update({'next': request.data.get('next', 'index')})
    return response