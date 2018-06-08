#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.conf import settings
from rest_framework.permissions import AllowAny

from base import resp
from base.views import BaseAPIView
from nmis.hospitals.models import Hospital, Staff, Doctor
from nmis.hospitals.serializers import HospitalSerializer
from nmis.hospitals.forms import StaffSignupForm

from .forms import HospitalSignupForm

logs = logging.getLogger(__name__)


class HospitalSignupView(BaseAPIView):
    """
    医疗机构注册, 也即医疗机构管理员注册
    """

    permission_classes = (AllowAny, )
    LOGIN_AFTER_SIGNUP = settings.LOGIN_AFTER_SIGNUP  # 默认注册后自动登录

    def post(self, req):
        form = HospitalSignupForm(req, data=req.data)

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

class HospitalView(BaseAPIView):
    """
    单个企业的get/update/delete操作
    """
    serializer_class = HospitalSerializer
    permission_classes = (AllowAny,)

    def get(self, req, hid):
        organ = self.get_object_or_404(hid, Hospital)
        return resp.serialize_response(organ, results_name='organ')

    def put(self, req, hid):
        """
        通过opt_type参数判定将对organ对象进行何种修改操作.
        opt_type='auth_approved' 为企业注册审核操作
        """
        opt_type = req.DATA.get('opt_type', '')
        if opt_type not in ('auth_approved', ):
            return resp.failed('请求参数错误')

        organ = Hospital.objects.get_cached(hid)
        if not organ:
            return resp.object_not_found()

        if opt_type == 'auth_approved':
            organ.accept()
            return resp.serialize_response(organ)

        # if opt_type == 'xxxx_option':
        #   do something...
        return resp.failed()


class StaffSignupView(BaseAPIView):
    """
    添加员工
    """
    permission_classes = (AllowAny)

    def post(self, req):
        form = StaffSignupForm(self, req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        staff = None

        try:
            staff = form.save()
        except Exception as e:
            logs.exception(e)
            return resp.failed(u'操作异常')




class StaffView(BaseAPIView):
    """
    单个员工删、查、改操作
    """
    permission_classes = (AllowAny,)

    def get(self, req, hid, dept_id, staff_id,):
        staff = self.get_object_or_404(staff_id, Staff)
        return resp.serialize_response(staff, results_name='staff')

    def put(self, req, staff_id):
        staff = self.get_object_or_404(staff_id, Staff)
        if not staff:
            return resp.object_not_found()
        staff.update(self,req.data)
        return resp.serialize_response(staff)

    def delete(self, req, staff_id):
        staff = self.get_object_or_404(staff_id, Staff,)
        if not staff:
            return resp.object_not_found()
        staff.delete()











