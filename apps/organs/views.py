#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.conf import settings
from django.db import transaction
from rest_framework.permissions import AllowAny, IsAuthenticated

from base import resp
from base.views import BaseAPIView
from base.common.decorators import check_id, check_params_not_null, check_params_not_all_null
from users.models import User
from utils import eggs

from .forms import OrganSignupForm
# from .models import Organ, Staff, Permission, Group
from .permissions import (
    IsOrganAdmin, OrganStaffPermission, UnloginStaffPermission
)

logs = logging.getLogger(__name__)


class OrganSignupView(BaseAPIView):
    """
    企业注册, 也即企业管理员注册
    """

    permission_classes = (AllowAny, )
    LOGIN_AFTER_SIGNUP = settings.LOGIN_AFTER_SIGNUP  # 默认注册后自动登录

    def post(self, req):
        form = OrganSignupForm(req, data=req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        organ = None
        try:  # DB操作较多
            organ = form.save()
        except Exception as e:
            logs.exception(e)
            return resp.failed(u'操作异常')

        if not self.LOGIN_AFTER_SIGNUP:  # 返回提示: 注册申请成功, 请等待审核...
            return resp.ok('申请成功, 请耐心等待审核结果')

        admin_user = organ.user
        admin_user.handle_login(req)
        token = admin_user.get_authtoken()
        if not token:
            return resp.lean_response('authtoken_error')

        response = resp.ok({
            'user_id': admin_user.id, 'organ_name': organ.name, 'organ_id': organ.id
        })
        response.data.update({'authtoken': token})
        return response









