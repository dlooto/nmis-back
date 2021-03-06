#coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.db.models import ProtectedError
from django.db.models.query import QuerySet

from base.common.decorators import check_params_not_all_null, check_params_not_null
from django.conf import settings
from django.db import transaction

from base.common.param_utils import get_id_list
from base.resp import Response
from nmis.devices.models import RepairOrder
from nmis.devices.permissions import AssertDeviceAdminPermission
from nmis.hospitals.serializers import StaffSerializer, RoleSerializer, \
    DepartmentStaffsCountSerializer, StaffWithRoleSerializer
from nmis.projects.models import ProjectPlan
from users.models import User

from utils.files import ExcelBasedOXL

from base import resp
from base.views import BaseAPIView
from nmis.hospitals.forms import StaffUpdateForm, StaffBatchUploadForm, \
    DepartmentBatchUploadForm, RoleCreateForm, RoleUpdateForm, \
    HospitalAddressCreateForm, HospitalAddressUpdateForm
from nmis.hospitals.permissions import IsHospSuperAdmin, HospitalStaffPermission, \
    ProjectDispatcherPermission, IsSuperAdmin, SystemManagePermission
from nmis.hospitals.models import Hospital, Department, Staff, Role, HospitalAddress
from .forms import (
    HospitalSignupForm,
    DepartmentUpdateFrom,
    StaffSignupForm,
    DepartmentCreateForm
)

from nmis.hospitals.consts import UPLOADED_STAFF_EXCEL_HEADER_DICT, \
    UPLOADED_DEPT_EXCEL_HEADER_DICT, ARCHIVE, ROLE_CODE_MAINTAINER

logger = logging.getLogger(__name__)


class HospitalSignupView(BaseAPIView):
    """
    医疗机构注册, 也即医疗机构管理员注册
    """

    permission_classes = (IsHospSuperAdmin, IsSuperAdmin)
    LOGIN_AFTER_SIGNUP = settings.LOGIN_AFTER_SIGNUP  # 默认注册后自动登录

    def post(self, req):
        self.check_object_any_permissions(req, None)
        form = HospitalSignupForm(req, data=req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        organ = None
        try:  # DB操作较多
            organ = form.save()
        except Exception as e:
            logger.exception(e)
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
    permission_classes = (IsHospSuperAdmin, IsSuperAdmin)

    def get(self, req, hid):
        self.check_object_any_permissions(req, None)

        organ = self.get_object_or_404(hid, Hospital)
        return resp.serialize_response(organ, results_name='organ')

    def put(self, req, hid):
        """
        通过opt_type参数判定将对organ对象进行何种修改操作.
        opt_type='auth_approved' 为企业注册审核操作
        """
        self.check_object_any_permissions(req, None)

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


class HospitalGlobalDataView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req, hid):
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, hospital)

        # 医院所有科室
        depts = hospital.get_all_depts()
        response = resp.serialize_response(depts, results_name='depts')

        # 医院所有项目流程
        flows = hospital.get_all_flows()
        response.data.update({"flows": resp.serialize_data(flows)})

        # 权限组
        # perm_groups = hospital.get_all_groups()
        # response.data.update({"perm_groups": resp.serialize_data(perm_groups)})

        roles = Role.objects.get_all_roles()
        response.data.update({"roles": resp.serialize_data(roles)})

        # 我负责的项目数量
        performer_project_count = ProjectPlan.objects.get_my_performer_projects(hospital, req.user.get_profile()).count()
        # 我协助的项目数量
        assistant_project_count = ProjectPlan.objects.get_my_assistant_projects(hospital, req.user.get_profile()).count()
        # 我申请的项目数量
        apply_project_count = ProjectPlan.objects.get_applied_projects(hospital, req.user.get_profile()).count()
        response.data.update(
            {
                "project_count": {
                    "performer_project_count": performer_project_count,
                    "assistant_project_count": assistant_project_count,
                    "apply_project_count": apply_project_count
                }
             }
        )
        # 我申请的保修单数量
        apply_repair_order_count = RepairOrder.objects.get_my_create_repair_order(req.user.get_profile()).count()
        # 处理中的保修单（我申请的保修单）
        dispose_repair_order_count = RepairOrder.objects.get_repair_order_in_repair(req.user.get_profile()).count()
        # 已完成的保修单
        complete_repair_order = RepairOrder.objects.get_completed_repair_order(req.user.get_profile()).count()
        response.data.update(
            {
                "repair_order_count": {
                    "apply_repair_order_count": apply_repair_order_count,
                    "dispose_repair_order_count": dispose_repair_order_count,
                    "complete_repair_order": complete_repair_order
                }
            }
        )
        return response


class StaffCreateView(BaseAPIView):
    """
    添加员工, 同时会为员工注册账号
    """
    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    @check_params_not_null(['username', 'staff_name', 'dept_id'])
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
        self.check_object_any_permissions(req, organ)
        dept = self.get_object_or_404(req.data.get('dept_id'), Department)
        form = StaffSignupForm(organ, dept, req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)

        staff = form.save()
        if not staff:
            return resp.failed('添加员工失败')
        staff_queryset = Staff.objects.filter(id=staff.id)
        staff_queryset = StaffSerializer.setup_eager_loading(staff_queryset)
        return resp.serialize_response(staff_queryset.first(), results_name='staff', srl_cls_name='StaffSerializer')


class StaffView(BaseAPIView):
    """
    单个员工删、查、改操作
    """
    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    def get(self, req, hid, staff_id):
        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, organ)

        staff = self.get_object_or_404(staff_id, Staff)
        staff_queryset = StaffSerializer.setup_eager_loading(Staff.objects.filter(id=staff_id))
        return resp.serialize_response(staff_queryset.first(), results_name='staff', srl_cls_name='StaffSerializer')

    def put(self, req, hid, staff_id):
        """
        变更员工信息
        """

        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, organ)

        # 判断变更的员工是否存在；
        staff = self.get_object_or_404(staff_id, Staff)

        if req.data.get('dept_id'):
            req.data.update({'dept': self.get_object_or_404(req.data.get('dept_id'), Department)})

        form = StaffUpdateForm(staff, req.data)

        if not form.is_valid():
            return resp.form_err(form.errors)
        updated_staff = form.save()
        staff_queryset = StaffSerializer.setup_eager_loading(Staff.objects.filter(id=staff_id))
        return resp.serialize_response(staff_queryset.first(), results_name='staff', srl_cls_name='StaffSerializer')

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
        self.check_object_any_permissions(req, organ)

        staff = self.get_object_or_404(staff_id, Staff)
        if req.user.get_profile().id == staff_id:
            return resp.failed("无权删除当前登录用户")
        user = staff.user
        # staff.clear_cache()
        # user.clear_cache()
        try:
            with transaction.atomic():
                staff.is_deleted = True
                staff.save()
                staff.cache()
                user.is_active = False
                user.save()
                user.cache()
                return resp.ok('删除成功')
        except Exception as e:
            logging.exception(e)
            return resp.failed("删除失败")


class StaffBatchDeleteView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, )

    @check_params_not_null(['staff_ids'])
    def delete(self, req, organ_id):
        """
        批量删除员工，同时删除员工账号
        """
        organ = self.get_object_or_404(organ_id, Hospital)
        self.check_object_any_permissions(req, organ)

        staff_ids = get_id_list(str(req.data.get('staff_ids', '')).strip())
        staffs = Staff.objects.filter(id__in=staff_ids)
        if not len(staffs) == len(staff_ids):
            return resp.failed('请确认是否有不存在员工')
        if req.user.get_profile() in staffs:
            return resp.failed('%s: %s' % (req.user.get_profile().name, '为当前登录用户，无法删除'))
        users = User.objects.filter(staff__in=staffs)
        try:
            with transaction.atomic():
                Staff.objects.clear_cache(staffs)
                User.objects.clear_cache(users)
                staffs.update(is_deleted=True)
                users.update(is_active=False)
                return resp.ok('删除成功')
        except ProtectedError as pe:
            logger.exception(pe)
            return resp.failed('存在员工有数据关联，无法删除')
        except Exception as e:
            logging.exception(e)
            return resp.failed("删除失败")


class StaffListView(BaseAPIView):

    permission_classes = (
        IsHospSuperAdmin, ProjectDispatcherPermission, SystemManagePermission
    )
    # permission_codes = ('GNS', 'GPA', 'GAD')
    # permission_classes = (CustomAnyPermission,)

    def get(self, req, hid):
        """
        查询某机构下员工列表(获取正常状态的员工)
        """
        # permission_codes = ('s', )
        # self.check_object_permissions(req, {'permission_codes': permission_codes})

        organ = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, organ)

        staff_list = organ.get_staffs(search_key=req.GET.get('search_key', '').strip())
        staff_list = StaffSerializer.setup_eager_loading(staff_list)
        # 分页查询员工列表
        return self.get_pages(staff_list, results_name='staffs', srl_cls_name='StaffSerializer')


class ChunkStaffListView(BaseAPIView):
    permission_classes = (
        IsHospSuperAdmin, ProjectDispatcherPermission, SystemManagePermission
    )

    def get(self, req, hid):
        """
        查询某机构下员工列表(附带用户角色、角色权限、和部门权限域信息)
        """
        organ = self.get_object_or_404(hid, Hospital)

        self.check_object_any_permissions(req, organ)

        staff_list = organ.get_staffs()
        staff_list = StaffWithRoleSerializer.setup_eager_loading(staff_list)
        # 分页查询员工列表
        return self.get_pages(staff_list, results_name='staffs', srl_cls_name='StaffWithRoleSerializer')


class StaffBatchUploadView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

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
        self.check_object_any_permissions(req, organ)

        file_obj = req.FILES.get('staff_excel_file')
        if not file_obj:
            return resp.failed('请选择要上传的文件')

        if file_obj.content_type in (ARCHIVE['.xls-wps'], ARCHIVE['.xls']):
            return resp.failed('系统不支持.xls格式的excel文件, 请使用正确的模板文件')
        elif file_obj.content_type not in (ARCHIVE['.xlsx'], ARCHIVE['.xlsx-wps'], ARCHIVE['.rar']):
            return resp.failed('系统不支持该类型文件，请使用正确的模板文件')

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

    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    @check_params_not_null(['name'])
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
        self.check_object_any_permissions(req, hospital)
        form = DepartmentCreateForm(hospital, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_dept = form.save()
        if not new_dept:
            return resp.failed('操作失败')
        return resp.serialize_response(new_dept, results_name='dept')


class DepartmentListView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, IsHospSuperAdmin, SystemManagePermission)

    def get(self, req, hid):
        """
        科室列表操作
        """
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, hospital)
        dept_list = hospital.get_all_depts()
        dept_list = DepartmentStaffsCountSerializer.setup_eager_loading(dept_list)
        return self.get_pages(
            dept_list, srl_cls_name='DepartmentStaffsCountSerializer', results_name='depts'
        )


class DepartmentView(BaseAPIView):
    """
    单个科室/部门的get/update/delete
    """
    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    def get(self, req, hid, dept_id):
        """
        查询单个科室详细信息
        :param req:
        :param hid: organ_id
        :return: 科室存在：返回科室详细信息，不存在科室：返回404
        """
        dept = self.get_object_or_404(dept_id, Department)
        hospital = self.get_object_or_404(hid, Hospital)
        self.check_object_any_permissions(req, hospital)

        return resp.serialize_response(dept, results_name='dept')

    @check_params_not_null(['name'])
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
        self.check_object_any_permissions(req, hospital)

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
        self.check_object_any_permissions(req, hospital)

        dept = self.get_object_or_404(dept_id, Department)
        # 查询当前科室是否存在员工
        if Staff.objects.get_by_dept(hospital, dept_id):
            return resp.failed('当前科室存在员工')

        dept.clear_cache()  # 清除缓存
        dept.delete()
        return resp.ok('操作成功')


class DepartmentBatchUploadView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

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
        self.check_object_any_permissions(req, organ)

        file_obj = req.FILES.get('dept_excel_file')
        if not file_obj:
            return resp.failed('请选择要上传的文件')

        if file_obj.content_type in (ARCHIVE['.xls-wps'], ARCHIVE['.xls']):
            return resp.failed('系统不支持.xls格式的excel文件, 请使用正确的模板文件')
        elif file_obj.content_type not in (ARCHIVE['.xlsx'], ARCHIVE['.xlsx-wps'], ARCHIVE['.rar']):
            return resp.failed('系统不支持该类型文件，请使用正确的模板文件')

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


class RoleCreateView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    @check_params_not_null(['name', 'permissions'])
    def post(self, req):
        self.check_object_any_permissions(req, None)

        form = RoleCreateForm(req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_role = form.save()
        if not new_role:
            return resp.failed('操作失败')
        return resp.serialize_response(new_role, srl_cls_name='ChunkRoleSerializer', results_name='role')


class RoleView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, IsHospSuperAdmin, SystemManagePermission)

    def get(self, req, role_id):
        self.check_object_any_permissions(req, None)

        role = self.get_object_or_404(role_id, Role)
        role_queryset = RoleSerializer.setup_eager_loading(Role.objects.filter(id=role_id)).first()
        return resp.serialize_response(role_queryset, srl_cls_name='RoleSerializer', results_name='role')

    @check_params_not_null(['name', 'permissions'])
    def put(self, req, role_id):
        self.check_object_any_permissions(req, None)

        role = self.get_object_or_404(role_id, Role)
        form = RoleUpdateForm(role, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_role = form.save()
        if not new_role:
            return resp.failed('操作失败')
        new_role = RoleSerializer.setup_eager_loading(Role.objects.filter(id=role_id)).first()
        return resp.serialize_response(new_role, srl_cls_name='ChunkRoleSerializer', results_name='role')

    def delete(self, req, role_id):
        self.check_object_any_permissions(req, None)
        role = self.get_object_or_404(role_id, Role)
        role.clear_cache()
        role.delete()
        return resp.ok("操作成功")


class RoleListView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission)

    def get(self, req):
        self.check_object_any_permissions(req, None)
        roles = Role.objects.all()
        roles = RoleSerializer.setup_eager_loading(roles)
        return resp.serialize_response(roles, srl_cls_name='ChunkRoleSerializer', results_name='roles')


class HospitalAddressListView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def get(self, req, hid):
        """
        获取医疗机构下资产设备存储地点列表
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        hospital_address_list = HospitalAddress.objects.get_hospital_address_list()
        return resp.serialize_response(hospital_address_list, results_name='hospital_addresses')


class HospitalAddressTreeView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def get(self, req, hid):
        """
        获取医疗机构下资产设备存储地点列表
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        address_tree = HospitalAddress.objects.get_tree()
        return Response(address_tree, results_name='hospital_addresses')


class StoragePlaceListView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def get(self, req, hid):
        """
        获取医疗机构下资产设备存储地点列表
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        storage_places = HospitalAddress.objects.get_storage_places()
        return resp.serialize_response(
            storage_places, results_name='hospital_addresses',
            srl_cls_name='BriefHospitalAddressSerializer'
        )


class HospitalAddressCreateView(BaseAPIView):

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def post(self, req, hid):
        """
        创建医院内部地址
        """
        self.check_object_any_permissions(req, None)
        hospital = self.get_object_or_404(hid, Hospital)
        form = HospitalAddressCreateForm(req.user.get_profile(), hospital, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        success, data = form.save()
        if not success:
            return resp.failed(data)
        return resp.serialize_response(data, results_name='hospital_address', srl_cls_name='HospitalAddressSerializer')


class HospitalAddressView(BaseAPIView):
    """单个医院内部地址"""

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def get(self, req, hid, address_id):
        """
        获取医院内部地址详情
        :param req:
        :param hid:
        :param address_id:
        :return:
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        address = self.get_object_or_404(address_id, HospitalAddress)
        return resp.serialize_response(address, results_name='hospital_address', srl_cls_name='HospitalAddressSerializer')

    def put(self, req, hid, address_id):
        """修改暂时仅修改详情,不修改地址的层级关系"""
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        old_address = self.get_object_or_404(address_id, HospitalAddress)
        form = HospitalAddressUpdateForm(req.user.get_profile(), old_address, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_address = form.save()
        if not new_address:
            return resp.failed('操作失败')
        return resp.serialize_response(new_address, results_name='hospital_address', srl_cls_name='HospitalAddressSerializer')

    def delete(self, req, hid, address_id):
        """
        删除单个医院内部地址
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        address = self.get_object_or_404(address_id, HospitalAddress)
        try:
            if address.has_children():
                return resp.failed(errors={'error_msg': '操作失败, 该地址下存在其他地址信息'})
            address.clear_cache()
            address.delete()
            return resp.ok('操作成功')
        except ProtectedError as pe:
            logger.exception(pe)
            return resp.failed(errors={'error_msg': '操作失败, 该地址存在业务关联'})
        except Exception as e:
            logger.exception(e)
            return resp.failed(errors={'error_msg': '操作失败'})


class HospitalAddressChildrenView(BaseAPIView):
    """单个医院内部地址"""

    permission_classes = (IsHospSuperAdmin, SystemManagePermission, AssertDeviceAdminPermission)

    def get(self, req, hid, address_id):
        """
        获取医院内部地址详情
        :param req:
        :param hid:
        :param address_id:
        :return:
        """
        self.check_object_any_permissions(req, None)
        self.get_object_or_404(hid, Hospital)
        address = self.get_object_or_404(address_id, HospitalAddress)
        children = address.children()
        return resp.serialize_response(children, results_name='hospital_addresses', srl_cls_name='HospitalAddressSerializer')


class SimpleStaffView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req, organ_id):
        """
        获取简单员工列表（供下拉菜单使用，只返回员工的ID，部门，姓名),对分配报修单中的员工列表只返回拥有维修工程师角色的列表
        """

        organ = self.get_object_or_404(organ_id, Hospital)
        self.check_object_permissions(req, organ)

        staff_list = organ.get_staffs(search_key=req.GET.get('search_key', '').strip())

        if req.GET.get('is_repair_man', '').strip() == 'True':
            staff_list = staff_list.filter(user__role__codename=ROLE_CODE_MAINTAINER)
        staff_list = StaffSerializer.setup_eager_loading(staff_list)
        # 分页查询员工列表
        return self.get_pages(staff_list, results_name='staffs', srl_cls_name='BriefStaffSerializer')