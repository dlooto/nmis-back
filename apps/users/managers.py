# coding=utf-8
#
# Created on Mar 21, 2014, by Junn
# 
#

import logging
from copy import deepcopy

from django.contrib.auth.models import BaseUserManager
from django.db import transaction
from django.utils import timezone

from base.models import BaseManager
from base import resp
from users.forms import is_valid_password, PASSWORD_ERROR_MSG

logs = logging.getLogger(__name__)


VALID_ATTRS = ('nickname', 'email', 'phone', 'gender', 'avatar')

AUTH_TYPE = {
    'P': 'phone',
    'U': 'username',
    'E': 'email',
}


class UserManager(BaseUserManager, BaseManager):
    """
    自定义UserManager
    """

    def create_param_user(self, auth_obj, password=None, is_active=False, commit=True,
                          **extra_fields):
        """
        可通过username/phone/email其中之一创建新用户账号.

        :param auth_obj: 元组类型, 如('email', 'hello@qq.com'), 或('phone', '15982021111')
                         由此确定用户账号注册类型
        :param password: 密码
        """
        now = timezone.now()
        user = self.model(is_staff=False, is_active=is_active, is_superuser=False,
                          last_login=now, date_joined=now, **extra_fields)
        setattr(user, auth_obj[0], auth_obj[1])
        user.set_password(password)
        if commit:
            user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """ 支持用Email创建管理员账号 """
        user = self.create_param_user(('email', email), password, is_active=True, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def is_exist(self, auth_obj):
        """
        判断phone/email/username是否已注册
        :param auth_obj: 参数形如  {'phone': 15910012003} 或 {'email': 'xj123@qq.com'}
        :return: 已注册则返回True, 否则返回False
        """
        if not isinstance(auth_obj, dict) or auth_obj.keys()[0] not in self.model.VALID_AUTH_FIELDS:
            logs.debug('参数格式错误: auth_obj %s' % auth_obj)
            return False

        try:
            # phone=phone or  username=username or email=email ...
            user = self.get(**auth_obj)
            return True
        except self.model.DoesNotExist:
            return False

    # TODO: 需要重构该方法, 将view层逻辑到views.py
    @staticmethod
    def reset_password(new_password, new_password_keyname, reset_key, reset_key_keyname,
            activate_user=False, activate_require=False, login_user=False, request=None):

        """
        :param new_password: 新密码
        :param reset_key: 重置密码使用的key
        :param activate_user: 是否激活用户
        :param activate_require: 是否需要用户为激活状态才能进行操作
        :param login_user: 是否在操作成功后登录该用户
        """
        from users.models import ResetRecord
        errors = {}

        if not is_valid_password(new_password):
            errors[new_password_keyname] = PASSWORD_ERROR_MSG
            return resp.form_err(errors)

        reset_record = ResetRecord.objects.filter(key=reset_key).first()
        if reset_record and reset_record.is_valid():
            user = reset_record.user
            if activate_require and (not user.is_active):
                errors['email'] = u'邮箱未激活'
                return resp.form_err(errors)

            # 操作成功
            with transaction.atomic():
                user.set_password(new_password)
                if activate_user:
                    user.is_active = True
                user.save()
                reset_record.set_invalid()
            response = resp.serialize_response(user, results_name='user')

            # 处理用户登录
            if login_user and request:
                logs.info('logging in user {}'.format(user))
                user.handle_login(request)
                from users.views import append_extra_info
                response = append_extra_info(user, request, response)
            return response

        errors[reset_key_keyname] = u'验证失败'
        return resp.form_err(errors)

    def assign_roles(self, users, new_roles, depts=None):
        from nmis.hospitals.models import UserRoleShip
        from nmis.hospitals.models import Role
        from nmis.hospitals.consts import ROLE_CODE_PRO_DISPATCHER

        ship_args = []
        old_ships = []
        same_ships = []
        pro_dispatcher_role = Role.objects.get_role_by_keyword(codename=ROLE_CODE_PRO_DISPATCHER)
        for user in users:
            for new_role in new_roles:
                ship_args.append(UserRoleShip(user=user, role=new_role))

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
        new_ships = deepcopy(ship_args)
        try:
            with transaction.atomic():

                if new_ships:
                    for ship in new_ships:
                        ship.save()
                        if depts and ship.role == pro_dispatcher_role:
                            ship.dept_domains.set(depts)
                        ship.cache()
                if old_ships:
                    for ship in old_ships:
                        ship.clear_cache()
                        ship.delete()
                if same_ships and depts:
                    for s in same_ships:
                        if s.role == pro_dispatcher_role:
                            s.dept_domains.set(depts)
                            s.cache
                return True, "操作成功"
        except Exception as e:
            logs.exception(e)
            return False, "操作失败"
