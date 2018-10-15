# coding=utf-8
#
# Created by junn, on 16/11/29
#

"""
Users view
"""
import copy
import logging

from django.db import transaction
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny

from base import codes
from base import resp
from base.authtoken import CustomToken
from base.common.decorators import check_not_null, check_params_not_null
from base.resp import LeanResponse
from base.views import BaseAPIView
from django.contrib.auth import logout as system_logout

from nmis.hospitals.models import Role, Department, UserRoleShip
from nmis.hospitals.serializers import SimpleRoleSerializer, SimplePermissionSerializer
from users.forms import UserSignupForm, UserLoginForm, CheckEmailForm
from users.models import User, ResetRecord
from utils.eggs import get_email_host_url

logs = logging.getLogger(__name__)


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
    authentication_classes = (TokenAuthentication, )
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

    def get(self, req):
        return resp.lean_response('method_not_allowed')


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


def append_extra_info(user, request, response):
    """
    用户登录成功后在 ``Response`` 中添加token, profile等其它数据

    :return: Response
    """

    token = user.get_authtoken()
    if not token:
        return resp.lean_response('authtoken_error')
    response.data.update({'authtoken': token})

    # 获取user.profile
    profile = user.get_profile()
    if not profile:
        return resp.failed(u'员工信息不存在，请联系管理员')
    response.data.update({'staff': resp.serialize_data(profile, srl_cls_name='SimpleStaffSerializer')})
    roles = user.get_roles()

    permissions = user.get_permissions()
    roles = SimpleRoleSerializer.setup_eager_loading(roles)
    permissions = SimplePermissionSerializer.setup_eager_loading(permissions)
    response.data.update({
        'roles': resp.serialize_data(roles, srl_cls_name='SimpleRoleSerializer'),
        "permissions":  resp.serialize_data(permissions, srl_cls_name='SimplePermissionSerializer')})

    # 设置登录成功后的跳转页面, 默认到index页
    response.data.update({'next': request.data.get('next', 'index')})
    return response


class AssignRolesDeptDomains(BaseAPIView):
    """
    给用户分配角色及权限域
    """
    permission_classes = (AllowAny,)

    @check_params_not_null(['role_ids', 'dept_domain_ids', 'user_ids'])
    def post(self, req):
        role_ids = req.data.get("role_ids")
        dept_domain_ids = req.data.get("dept_domain_ids")
        user_ids = req.data.get("user_ids")
        users = User.objects.filter(id__in=user_ids).all()
        roles = Role.objects.filter(id__in=role_ids).all()
        depts = Department.objects.filter(id__in=dept_domain_ids).all()
        if not users or not len(user_ids) == len(users):
            return resp.failed('含有不存在的用户')
        if not roles or not len(role_ids) == len(roles):
            return resp.failed('含有不存在的角色')
        if not depts or not len(dept_domain_ids) == len(depts):
            return resp.failed('含有不存在的部门')
        # 根据user和role查询数据是否已经存在UserRoleShip记录
        # 如果全部不存在，创建并保存
        # 如果全部存在，不做处理
        # 如果参数数据，比查询结果多，创建多出来的这部分
        # 如果参数数据，少于查询结果，删除少了的这部分

        old_ships = []
        ship_args = []
        same_ships = []
        for user in users:
            for role in roles:
                ship_args.append(UserRoleShip(user=user, role=role))

            old_ship_query = UserRoleShip.objects.filter(user=user).all()
            if old_ship_query:
                for query in old_ship_query:
                    old_ships.append(query)

        for ship_arg in ship_args[:]:
            for old_ship in old_ships[:]:
                if ship_arg.user.id == old_ship.user.id and ship_arg.role.id == old_ship.role.id:
                    ship_args.remove(ship_arg)
                    same_ships.append(old_ship)
                    old_ships.remove(old_ship)
        try:
            with transaction.atomic():

                if ship_args:
                    for ship in ship_args:
                        ship.save()
                        ship.cache()
                        ship.dept_domains.set(depts)
                if old_ships:
                    for ship in old_ships:
                        ship.clear_cache()
                        ship.dept_domains.set(depts)
                        ship.delete()
                if same_ships:
                    for s in same_ships:
                        s.dept_domains.set(depts)
                        s.cache
                return resp.ok("操作成功")
        except Exception as e:
            logs.info(e.__cause__)
            logs.exception(e)
            return resp.failed("操作失败")


