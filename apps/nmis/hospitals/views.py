#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from base.common.decorators import check_params_not_all_null, check_params_not_null
from django.conf import settings
from rest_framework.permissions import AllowAny

from base import resp
from base.views import BaseAPIView
from nmis.hospitals.models import Hospital, Department, Staff, Doctor
from nmis.hospitals.serializers import HospitalSerializer, StaffSerializer
from .forms import HospitalSignupForm, DepartmentUpdateForm, StaffSignupForm, DepartmentCreateForm

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


class StaffCreateView(BaseAPIView):
    """
    添加员工, 同时会为员工注册账号
    """
    permission_classes = (AllowAny, )

    @check_params_not_null(['username', 'password', 'staff_name', 'dept_id', 'staff_title'])
    def post(self, req, hid):
        """
        添加员工步骤:
            1. 创建user对象: 判断username无重复, 密码正确, ...
                先ceate user object, 再user.set_password(raw_password)
            2. 创建staff对象: 先赋值user, 再staff.save()
            3. 返回staff结果

        以下字段不能为空:
            usrname, password, staff_name, hid, dept_id,

        """

        objects = self.get_objects_or_404({'hid': Hospital, 'dept_id': Department})
        form = StaffSignupForm(objects['hid'], objects['dept_id'], req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        staff = form.save()
        if not staff:
            return resp.failed('添加员工失败')
        return resp.serialize_response(staff, result_name='staff')


class StaffView(BaseAPIView):
    """
    单个员工删、查、改操作
    """
    permission_classes = (AllowAny,)    # TODO: replaceed with IsHospitalAdmin...

    def get(self, req, hid, staff_id):
        staff = self.get_object_or_404(staff_id, Staff)
        return resp.serialize_response(staff, results_name='staff')

    def put(self, req, hid, staff_id):
        staff = self.get_object_or_404(staff_id, Staff)
        staff.update(self, req.data)
        return resp.serialize_response(staff)

    def delete(self, req, hid, staff_id):
        staff = self.get_object_or_404(staff_id, Staff)
        staff.delete()
        return resp.ok('删除成功')


class StaffListView(BaseAPIView):

    def get(self, req, hid):
        pass


class DepartmentCreateView(BaseAPIView):

    permission_classes = (AllowAny, )

    @check_params_not_null(['name', 'attri'])
    def post(self, req, hid):
        """
        创建科室
        参数格式示例如下:
        {
            "name": "妇产科",  # 科室名称
            "contact": "18999999998",  # 科室电话
            "attri": "SU",  # 科室属性
            "desc": "负责产科和妇科相关医疗工作"    # 科室描述
            "organ": 20180606 # 医院ID
        }
        """

        hospital = self.get_object_or_404(hid, Hospital)

        form = DepartmentCreateForm(req.data, hospital)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_dept = form.save()
        if not new_dept:
            return resp.failed('操作失败')
        return resp.serialize_response(new_dept, results_name='dept')


class DepartmentListView(BaseAPIView):

    permission_classes = (AllowAny, )

    def get(self, req, hid):
        """
        科室列表操作
        """

        dept_list = Department.objects.get_queryset()
        return resp.serialize_response(dept_list, results_name='dept')


class DepartmentView(BaseAPIView):
    """
    单个科室/部门的get/update/delete
    """
    permission_classes = (AllowAny, )  # TODO: 替换为IsHospitalAdmin

    def get(self, req, hid, dept_id):
        """
        查询单个科室详细信息
        :param req:
        :param hid: hospital_id
        :return: 科室存在：返回科室详细信息，不存在科室：返回404
        """
        dept = self.get_object_or_404(dept_id, Department)
        return resp.serialize_response(dept, results_name='dept')

    @check_params_not_all_null(['name', 'contact', 'attri', 'desc'])
    def put(self, req, hid, dept_id,):
        """
        修改单个科室详细信息
        参数格式示例如下:
        {
            "name": "设备科", # 科室名称
            "contact": "18999999999",
            "attri": "SU",
            "desc": "负责医院设备采购，维修，"
        }
        """

        dept = self.get_object_or_404(dept_id, Department)
        form = DepartmentUpdateForm(dept, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        updated_dept = form.save()
        return resp.serialize_response(updated_dept, results_name='dept')

    def delete(self, req, hid, dept_id):
        """
        删除科室，操作成功返回如下json格式
        {
            "code": 10000,
            "msg":  "ok"
        }
        """
        dept = self.get_object_or_404(dept_id, Department)
        dept.clear_cache()  # 清除缓存
        dept.delete()
        return resp.ok('操作成功')








