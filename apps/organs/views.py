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

from .forms import OrganSignupForm, OrganLoginForm
from .models import Organ, Staff, Permission, Group
from .permissions import (
    IsOrganAdmin, OrganStaffPermission, HRPermission, UnloginStaffPermission
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


class OrganLoginView(BaseAPIView):
    """
    企业管理员登录.  已弃用 !
    """

    permission_classes = (AllowAny, )
    organ_login_next = 'organ_index'

    def post(self, req):
        form = OrganLoginForm(req, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)

        user = form.login(req)
        response = resp.serialize_response(user, results_name='user')

        token = user.get_authtoken()
        if not token:
            return resp.lean_response('authtoken_error')

        response.data.update({'authtoken': token})

        # 设置登录成功后的跳转页面
        if user.get_profile().is_organ_admin():
            response.data.update({'next': self.organ_login_next,
                                  'organ_id': user.organ.id,
                                  })
        return response


class OrganSignupActivationView(BaseAPIView):
    """
    企业注册激活
    """

    permission_classes = (AllowAny,)

    def post(self, req):
        """
        激活将置user.is_active=True

        :return: 成功后返回 resp.ok()
        """
        new_password_keyname = 'new_password'
        activation_key_keyname = 'activation_key'

        activation_key = req.data.get(activation_key_keyname)
        new_password = req.data.get(new_password_keyname)

        response = User.objects.reset_password(
            new_password=new_password,
            new_password_keyname=new_password_keyname,
            reset_key=activation_key,
            reset_key_keyname=activation_key_keyname,
            activate_user=True,
            login_user=True,
            request=req,
        )

        return response


class OrganView(BaseAPIView):
    """
    单个企业的get/update/delete操作
    """

    def get(self, req, organ_id):
        organ = self.get_object_or_404(organ_id, Organ)
        return resp.serialize_response(organ, results_name='organ')

    def put(self, req, organ_id):
        """
        通过opt_type参数判定将对organ对象进行何种修改操作.
        opt_type='auth_approved' 为企业注册审核操作
        """
        opt_type = req.DATA.get('opt_type', '')
        if opt_type not in ('auth_approved', ):
            return resp.failed('请求参数错误')

        organ = Organ.objects.get_cached(organ_id)
        if not organ:
            return resp.object_not_found()

        if opt_type == 'auth_approved':
            organ.accept()
            return resp.serialize_response(organ)

        # if opt_type == 'xxxx_option':
        #   do something...
        return resp.failed()

    def delete(self, req, organ_id):
        pass


class StaffListView(BaseAPIView):
    """
    员工信息批量查询,分组员工列表,待邀请员工列表(group_id=0)
    """
    permission_classes = [UnloginStaffPermission, OrganStaffPermission]

    def get(self, req, organ_id):
        """
        :param organ_id: 企业id
        """
        organ = self.get_object_or_404(organ_id, Organ)
        self.check_object_any_permissions(req, organ)
        group_id = req.GET.get('group_id', None)
        pending_active = eggs.to_bool(req.GET.get('pending_active', '').strip())

        if pending_active:
            staff_list = organ.get_all_staffs()
            staffs = staff_list.filter(user__is_active=False)
        elif group_id:
            group = self.get_object_or_404(group_id, Group)
            staffs = organ.get_staffs_in_group(group)
        else:
            staffs = organ.get_all_staffs()
        return resp.serialize_response(staffs, results_name='staffs')


class StaffView(BaseAPIView):
    """
    单个员工操作
    """

    permission_classes = [HRPermission,]

    def get(self, req, staff_id):
        """
        返回指定的员工信息,暂时实现展示登录进来的用户信息,其他人信息不能展示,staff_id暂时没有使用
        :param staff_id: 员工id
        """
        try:
            response = resp.serialize_response(req.user.staff, results_name='staff')
            response.data.update({'user_email': req.user.email})
            return response
        except Staff.DoesNotExist:
            return resp.object_not_found()
        except Exception as e:
            logs.exception(e)
            return resp.failed('操作异常')

    @check_params_not_null(['name', 'contact'])
    @check_params_not_all_null(['group_id', 'title'])
    def put(self, req, staff_id):
        """ 员工修改个人信息 """
        name = req.data.get('name', '')
        contact = req.data.get('contact', '')
        title = req.data.get('title', '')
        group_id = req.data.get('group_id')
        if not (title or group_id):
            return resp.params_err({'title': u'参数为空'})
        if group_id:  # 存在group_id,意味着是管理员在修改信息
            user_staff = req.user.get_profile()
            self.check_object_permissions(req, user_staff.organ)
            staff = self.get_object_or_404(staff_id, Staff)
            group = self.get_object_or_404(group_id, Group)
            # 不允许修改自己的权限分组
            if user_staff.id == staff.id and user_staff.group.id != group.id:
                return resp.failed(u'禁止修改自己的分组')
            if not user_staff.is_organ_admin() and staff.group.id != group.id:
                return resp.failed(u'禁止修改分组')
            staff.name = name
            staff.group = group
            staff.contact = contact
            staff.save()
            return resp.ok(u'个人信息修改成功')

        # 用户修改自己的信息
        try:
            staff = req.user.get_profile()
            staff.name = name
            staff.contact = contact
            staff.title = title
            staff.save()
            return resp.ok(u'个人信息修改成功')
        except Staff.DoesNotExist:
            return resp.object_not_found()

    def delete(self, req, staff_id):
        # 没有登录的uer 没有 get_profile 属性, 确保安全.
        if not req.user.is_authenticated or not req.user.get_profile().is_organ_admin():
            return self.permission_denied(req, u'没有权限的操作.')
        staff = self.get_object_or_404(staff_id, Staff)
        login_staff = req.user.get_profile()
        if staff == login_staff:
            return resp.failed(u'不能删除自己')
        if login_staff.organ != staff.organ:
            return resp.failed(u'非法操作')
        staff.set_delete()
        return resp.ok(u'删除成功')


class StaffCreateView(BaseAPIView):
    """
    创建企业员工. 需要企业管理员权限
    """

    permission_classes = [IsOrganAdmin, ]

    @check_params_not_null(['name', 'contact', 'email', 'group_id'])
    @check_id('group_id')
    def post(self, req, organ_id):
        organ = self.get_object_or_404(organ_id, Organ)
        self.check_object_permissions(req, organ)  # use this to check permission

        name = req.data.get('name', '')
        contact = req.data.get('contact', '')
        email = req.data.get('email', '').lower()
        group_id = req.data.get('group_id')

        group = self.get_object_or_404(group_id, Group)
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return resp.failed(u'邮箱已注册')
        except User.DoesNotExist:
            with transaction.atomic():
                user = User.objects.create_param_user(('email', email), is_active=False)
                staff = organ.create_staff(user, name, email, contact, group=group)
        else:  # 恢复系统中存在的用户
            staff = user.get_profile()
            staff.add_to_organ(name, contact, organ, group)

        if staff.is_st_or_in_group():
            return resp.ok(u'添加成功')

        return resp.ok(u'添加成功. 请到邮箱激活账户')


class PermissionListView(BaseAPIView):
    """返回可用权限列表"""

    def get(self, req, organ_id):
        perms = Permission.objects.get_all()
        return resp.serialize_response(perms, results_name='perms')


class GroupCreateView(BaseAPIView):
    """为指定企业创建权限组"""

    permission_classes = [IsOrganAdmin, ]

    def post(self, req, organ_id):
        organ = Organ.objects.get_cached(organ_id)
        self.check_object_permissions(req, organ)

        group_name = req.data.get('name')
        group_desc = req.data.get('desc', '')
        perm_list = req.data.get('perm_list')

        group = organ.create_group(**{'name': group_name, 'desc': group_desc})
        group.set_permissions(perm_list)

        return resp.serialize_response(group, results_name='group')


class GroupListView(BaseAPIView):
    """返回指定企业的所有权限组"""
    permission_classes = [HRPermission, ]

    def get(self, req, organ_id):
        organ = Organ.objects.get_cached(organ_id)
        self.check_object_permissions(req, organ)
        return resp.serialize_response(organ.get_all_groups(), results_name='groups')


class OrganGlobalDataListView(BaseAPIView):
    """
    返回企业全局数据列表:
        企业信息, 企业部门信息, 企业全局配置数据等
    """
    permission_classes = [OrganStaffPermission, ]

    def get(self, req, organ_id):
        organ = self.get_object_or_404(organ_id, Organ)
        self.check_object_permissions(req, organ)

        # 企业信息
        response = resp.serialize_response(organ, results_name='organ')

        # 企业部门列表
        departments = organ.get_all_departments()
        response.data.update({"departments": resp.serialize_data(departments)})

        # 企业成员列表
        staffs = organ.get_all_staffs()
        response.data.update({"staffs": resp.serialize_data(staffs)})

        return response


class OrganHomeView(BaseAPIView):
    """
    机构首页
    """

    def get(self, req, organ_id):
        return resp.ok()








