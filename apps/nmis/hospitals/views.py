#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging
from operator import eq

from django.contrib.auth.decorators import permission_required

from base.common.decorators import check_params_not_all_null, check_params_not_null
from base.common.param_utils import get_id_list
from django.conf import settings
from django.db import transaction
from rest_framework.permissions import AllowAny
from utils.files import ExcelBasedOXL

from base import resp
from base.views import BaseAPIView
from nmis.hospitals.forms import StaffUpdateForm, StaffBatchUploadForm, \
    DepartmentBatchUploadForm, RoleCreateForm
from nmis.hospitals.permissions import IsHospitalAdmin, HospitalStaffPermission, \
    ProjectDispatcherPermission
from nmis.hospitals.models import Hospital, Department, Staff, Group, Role
from .forms import (
    HospitalSignupForm,
    DepartmentUpdateFrom,
    StaffSignupForm,
    DepartmentCreateForm
)

from nmis.hospitals.consts import UPLOADED_STAFF_EXCEL_HEADER_DICT, \
    UPLOADED_DEPT_EXCEL_HEADER_DICT, ARCHIVE

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

        organ = self.get_object_or_404(hid)

        if opt_type == 'auth_approved':
            organ.accept()
            return resp.serialize_response(organ)

        return resp.failed()


class HospitalGlobalDataView(BaseAPIView):

    permission_classes = [HospitalStaffPermission, ]

    def get(self, req, hid):
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)

        # 医院所有科室
        depts = hospital.get_all_depts()
        response = resp.serialize_response(depts, results_name='depts')

        # 医院所有项目流程
        flows = hospital.get_all_flows()
        response.data.update({"flows": resp.serialize_data(flows)})

        # 权限组
        perm_groups = hospital.get_all_groups()
        response.data.update({"perm_groups": resp.serialize_data(perm_groups)})

        #

        return response


class StaffCreateView(BaseAPIView):
    """
    添加员工, 同时会为员工注册账号
    """
    permission_classes = (IsHospitalAdmin, )

    @check_params_not_null(['username', 'password', 'staff_name', 'dept_id'])
    def post(self, req, hid):
        """
        添加员工步骤:
            1. 创建user对象: 判断username无重复, 密码正确, ...
                先ceate user object, 再user.set_password(raw_password)
            2. 创建staff对象: 先赋值user, 再staff.save()
            3. 返回staff结果

        以下字段不能为空:
            username, password, staff_name, hid, dept_id,

        """
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)
        dept = self.get_object_or_404(req.data.get('dept_id'), Department)
        form = StaffSignupForm(organ, dept, req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        staff = form.save()
        if not staff:
            return resp.failed('添加员工失败')
        return resp.serialize_response(staff, results_name='staff')


class StaffsPermChangeView(BaseAPIView):
    """
    同时修改多个职员的权限为新的一种权限
    """
    permission_classes = (IsHospitalAdmin, )

    @check_params_not_null(['perm_group_id', 'staffs'])
    def put(self, req, hid):
        """

        the request param Example:
        {
            "perm_group_id": 1001,
            "staffs": "2001,2002,2003"
        }

        """
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)
        perm_group = self.get_objects_or_404({'perm_group_id': Group}).get('perm_group_id')

        staff_id_list = get_id_list(req.data.get('staffs'))
        if req.user.get_profile().id in staff_id_list:
            return resp.failed('无权修改自身权限')
        if Staff.objects.filter(id__in=staff_id_list).count() < len(staff_id_list):
            return resp.failed('请确认是否有不存在的员工信息')
        staffs = Staff.objects.filter(id__in=staff_id_list)
        staffs.update(group=perm_group)
        for staff in staffs:
             staff.cache()
        return resp.ok('员工权限已修改')


class StaffView(BaseAPIView):
    """
    单个员工删、查、改操作
    """
    permission_classes = (IsHospitalAdmin, )

    def get(self, req, hid, staff_id):
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)

        staff = self.get_object_or_404(staff_id, Staff)
        return resp.serialize_response(staff, results_name='staff')

    def put(self, req, hid, staff_id):
        """
        变更员工信息
        """

        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)

        # 判断变更的员工是否存在；
        staff = self.get_object_or_404(staff_id, Staff)

        if req.data.get('dept_id'):
            req.data.update({'dept': self.get_object_or_404(req.data.get('dept_id'), Department)})

        form = StaffUpdateForm(staff, req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)
        updated_staff = form.save()
        return resp.serialize_response(updated_staff, results_name='staff')

    def delete(self, req, hid, staff_id):
        """
        删除员工，同时删除用户账号信息,
        如果存在其他关联数据导致删除失败，目前直接返回删除失败
        :param req: http请求
        :param hid: organ_id 机构ID
        :param staff_id:
        :return:
        """
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)

        staff = self.get_object_or_404(staff_id, Staff)
        if req.user.get_profile().id == staff_id:
            return resp.failed("无权删除本人信息")
        user = staff.user
        staff.clear_cache()
        user.clear_cache()
        try:
            with transaction.atomic():
                staff.delete()
                user.delete()
                return resp.ok('删除成功')
        except Exception as e:
            logging.exception(e)
            return resp.failed("删除失败")


class StaffListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission, HospitalStaffPermission)

    def get(self, req, hid):
        """
        查询某机构下员工列表
        """
        organ = self.get_object_or_404(hid, Hospital)

        self.check_object_any_permissions(req, organ)

        staff_list = organ.get_staffs()
        return resp.serialize_response(staff_list, results_name='staffs')


class StaffBatchUploadView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    @check_params_not_null(['staff_excel_file'])
    def post(self, req, hid):
        """
        批量导入某机构的员工信息
        :param req:
        :param hid:
        :return:

        TODO：先实现文件上传解析功能，再补充校验
        检查文件格式，目前仅支持xlsx格式
        检查医疗机构是否存在
        检查科室列表是否存在
        检查excel文档中员工用户名是否有重复数据
        检查员工用户名是否存在

        """
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)

        file_obj = req.FILES.get('staff_excel_file')
        if not file_obj:
            return resp.failed('请选择要上传的文件')

        if not ARCHIVE['.xlsx'] == file_obj.content_type:
            return resp.failed('导入文件不是Excel文件，请检查')

        # 将文件存放到服务器
        # import os
        # file_server_path = open(os.path.join('/media/', '', file_obj.name), 'wb')
        # file = open('file_server_path', 'wb')

        is_success, ret = ExcelBasedOXL.open_excel(file_obj)
        if not is_success:
            return resp.failed(ret)

        head_dict = UPLOADED_STAFF_EXCEL_HEADER_DICT
        success, result = ExcelBasedOXL.read_excel(ret, head_dict)
        ExcelBasedOXL.close(ret)
        if not success:
            return resp.failed(result)

        form = StaffBatchUploadForm(organ, result)
        if not form.is_valid():
            return resp.form_err(form.errors)

        return resp.ok('导入员工信息成功') if form.save() else resp.failed('导入失败')


class DepartmentCreateView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )
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
        self.check_object_permissions(req, hospital)    # 验证权限
        form = DepartmentCreateForm(hospital, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_dept = form.save()
        if not new_dept:
            return resp.failed('操作失败')
        return resp.serialize_response(new_dept, results_name='dept')


class DepartmentListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    def get(self, req, hid):
        """
        科室列表操作
        """
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)
        dept_list = hospital.get_all_depts()
        return resp.serialize_response(
            dept_list, srl_cls_name='DepartmentStaffsCountSerializer', results_name='dept'
        )


class DepartmentView(BaseAPIView):
    """
    单个科室/部门的get/update/delete
    """
    permission_classes = (IsHospitalAdmin, )

    def get(self, req, hid, dept_id):
        """
        查询单个科室详细信息
        :param req:
        :param hid: organ_id
        :return: 科室存在：返回科室详细信息，不存在科室：返回404
        """
        dept = self.get_object_or_404(dept_id, Department)

        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)

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
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)

        dept = self.get_object_or_404(dept_id, Department)
        form = DepartmentUpdateFrom(dept, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        updated_dept = form.save()
        return resp.serialize_response(updated_dept, results_name='dept')

    def delete(self, req, hid, dept_id):
        """
        删除科室，科室存在员工不能删除
        操作成功返回如下json格式
        {
            "code": 10000,
            "msg":  "ok"
        }
        """
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)

        dept = self.get_object_or_404(dept_id, Department)
        # 查询当前科室是否存在员工
        if Staff.objects.get_by_dept(hospital, dept_id):
            return resp.failed('当前科室存在员工')

        dept.clear_cache()  # 清除缓存
        dept.delete()
        return resp.ok('操作成功')


class DepartmentBatchUploadView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    @check_params_not_null(['dept_excel_file'])
    def post(self, req, hid):
        """
        批量导入某机构的部门信息
        :param req:
        :param hid:
        :return:

        TODO：先实现文件上传解析功能，再补充校验
        检查文件格式，目前仅支持xlsx格式
        检查科室列表是否存在
        检查科室是否有重复数据
        """
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, organ)

        file_obj = req.FILES.get('dept_excel_file')
        if not file_obj:
            return resp.failed('请选择要上传的文件')

        if not ARCHIVE['.xlsx'] == file_obj.content_type:
            return resp.failed('导入文件不是Excel文件，请检查')

        # 将文件存放到服务器
        # import os
        # file_server_path = open(os.path.join('/media/', '', file_obj.name), 'wb')
        # file = open('file_server_path', 'wb')

        is_success, ret = ExcelBasedOXL.open_excel(file_obj)
        if not is_success:
            return resp.failed(ret)

        head_dict = UPLOADED_DEPT_EXCEL_HEADER_DICT
        success, result = ExcelBasedOXL.read_excel(ret, head_dict)
        ExcelBasedOXL.close(ret)
        if not success:
            return resp.failed(result)

        form = DepartmentBatchUploadForm(organ, result)
        if not form.is_valid():
            return resp.form_err(form.errors)

        return resp.ok('导入成功') if form.save() else resp.failed('导入失败')


class GroupListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    def get(self, req, hid):
        """
        获取权限组集合
        """
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_permissions(req, hospital)
        groups_list = hospital.get_all_groups()
        return resp.serialize_response(groups_list, results_name='group')


class RoleCreateView(BaseAPIView):

    def post(self, req):

        form = RoleCreateForm(req.data)
        role = Role.objects.filter(name=req.data.get('name'))
        if not role:
            resp.failed("角色已存在")
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_role = form.save()
        if not new_role:
            return resp.failed('操作失败')
        return resp.serialize_response(new_role, srl_cls_name='ChunkRoleSerializer', results_name='role')


class RoleView(BaseAPIView):

    def get(self, req, role_id):
        role = self.get_object_or_404(role_id, Role)
        return resp.serialize_response(role, srl_cls_name='RoleSerializer', results_name='role')

    def delete(self, req, role_id):
        role = self.get_object_or_404(role_id, Role)
        role.clear_cache()
        role.delete()
        return resp.ok("操作成功")


class RoleListView(BaseAPIView):
    permission_classes = (IsHospitalAdmin, )

    def get(self, req):
        roles = Role.objects.all()
        return resp.serialize_response(roles, srl_cls_name='ChunkRoleSerializer', results_name='roles')
