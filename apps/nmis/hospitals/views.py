#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response

from base import resp
from base.views import BaseAPIView
from nmis.hospitals.models import Hospital, Department

from .forms import HospitalSignupForm, DepartmentUpdateFrom

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


class DepartView(BaseAPIView):
    """
    单个科室/部门的get/update/delete
    """
    permission_classes = (AllowAny,)

    def get(self, req, hid, dept_id):
        """
        查询单个科室详细信息
        :param req:
        :param hid: 科室id
        :return: 科室存在：返回科室详细信息，不存在科室：返回404
        """
        dept = self.get_object_or_404(dept_id, Department)
        return resp.serialize_response(dept, results_name='dept')

    def put(self, req, hid, dept_id,):
        """
        修改单个科室详细信息
        参数格式示例如下:
        {
            "name": "设备科",
            "contact": "18999999999",
            "attri": "SU",
            "desc": "负责医院设备采购，维修，"
        }
        :param req:
        :param hid:
        :param dept_id: 科室ID
        :return:
        """

        data = req.data
        if not data:
            return resp.string_response('参数为null')
        form = DepartmentUpdateFrom(data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        form.save()
        dept = Department.objects.get(id=dept_id)
        return resp.serialize_response(dept, results_name='dept')

    def delete(self, req, hid, dept_id):
        """
        删除科室，操作成功返回如下json格式
        {
            "code": 10000,
            "msg":  "ok"
        }
        :param req:
        :param hid: 医院ID
        :param dept_id: 科室ID
        :return:
        """
        dept = Department.objects.get(pk=dept_id)
        dept.delete()
        return resp.ok()

