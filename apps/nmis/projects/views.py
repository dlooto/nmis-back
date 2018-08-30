# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging
from collections import OrderedDict
from base import resp
from base.common.decorators import (
    check_id, check_id_list, check_params_not_null, check_params_not_all_null
)

from base.views import BaseAPIView

from nmis.devices.models import OrderedDevice, SoftwareDevice
from nmis.hospitals.models import Hospital, Staff, Department
from nmis.hospitals.permissions import (
    HospitalStaffPermission, IsHospitalAdmin, ProjectDispatcherPermission
)
from nmis.projects.forms import (
    ProjectPlanCreateForm,
    ProjectPlanUpdateForm,
    OrderedDeviceCreateForm,
    OrderedDeviceUpdateForm,
    ProjectFlowCreateForm,
    ProjectFlowUpdateForm, )
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone
from nmis.projects.permissions import ProjectPerformerPermission
from nmis.projects.serializers import ChunkProjectPlanSerializer, ProjectPlanSerializer

from nmis.hospitals.consts import (
    GROUP_CATE_PROJECT_APPROVER,
    GROUP_CATE_NORMAL_STAFF
)
from nmis.projects.consts import (
    PROJECT_STATUS_CHOICES,
    PRO_STATUS_STARTED,
    PRO_STATUS_DONE,
    PRO_STATUS_PENDING,
    FLOW_UNDONE,
    PROJECT_CATE_CHOICES,
    PRO_CATE_HARDWARE,
    PRO_CATE_SOFTWARE,
    PRO_STATUS_OVERRULE,
    PRO_OPERATION_OVERRULE)

logs = logging.getLogger(__name__)


class ProjectPlanListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, HospitalStaffPermission, ProjectDispatcherPermission)

    @check_params_not_null(['organ_id', 'type'])
    def get(self, req):
        """
        获取项目列表，包括：我申请的项目，待分配的项目、项目总览、我负责的项目
        参数列表：
            type:       string    项目类型
            organ_id:   int       当前医院ID
            pro_status: string    项目状态（PE：未启动，SD：已启动，DO：已完成，OR：已驳回，PA：已挂起）,为None查看全部
            search_key: string    项目名称/项目申请人关键字
        """
        hospital = self.get_object_or_404(req.GET.get('organ_id'), Hospital)

        action_type = req.GET.get("type", '').strip()
        # 判断操作类型
        if action_type not in ('undispatch', 'total_projects', 'apply', 'my_performer'):
            return resp.form_err({'type': '不存在的操作类型'})

        status = req.GET.get('pro_status', '').strip()
        # 项目状态校验
        if status:
            if status not in dict(PROJECT_STATUS_CHOICES):
                return resp.form_err({'err_status': '项目状态异常'})

        # 获取当前登录系统用户
        login_staff = req.user.get_profile()
        search_key = req.GET.get('search_key', '').strip()
        # 根据关键字查询staffs集合
        staffs = None
        if search_key:
            staffs = Staff.objects.get_by_name(hospital, search_key)

        if action_type == 'undispatch':
            # 判断当前员工是否为项目分配者权限，否则检查是否为管理权限
            if not (login_staff.group.cate == GROUP_CATE_PROJECT_APPROVER):
                self.check_object_permissions(req, hospital)

            result_data = self.get_undispatch_project_list(req, hospital=hospital)

        elif action_type == 'total_projects':
            # 检查管理员权限,只允许管理员操作
            self.check_object_permissions(req, hospital)
            result_data = self.get_total_project_list(
                search_key, status, staffs=staffs, hospital=hospital)

        else:
            self.check_object_any_permissions(req, hospital)
            result_data = self.get_performer_or_apply_project_list(
                req, search_key, status, action_type, hospital=hospital, login_staff=login_staff,
                staffs=staffs
            )
        return self.response_project_list(**result_data)

    def get_undispatch_project_list(self, req, hospital=None):
        """
        所有待分配的项目列表
        """
        # 获取权限组ID
        group_id_list = [group.id for group in req.user.get_permissions()]
        # 获取权限域中部门ID
        dept_id_list = self.get_user_role_dept_domains(req, group_id_list)

        result_projects = ProjectPlan.objects.get_undispatched_projects(dept_id_list, hospital)
        status_count = ProjectPlan.objects.get_group_by_status(
            status=PRO_STATUS_PENDING)

        return self.get_projects_and_status_count_data(result_projects, status_count)

    def get_total_project_list(self, search_key, status, hospital=None, staffs=None):
        """
        获取项目总览列表
        """
        # 获取项目各状态条数
        status_count = ProjectPlan.objects.get_group_by_status(search_key=search_key)

        result_projects = ProjectPlan.objects.get_by_search_key(
            hospital, project_title=search_key, performers=staffs, status=status
        )

        return self.get_projects_and_status_count_data(result_projects, status_count)

    def get_performer_or_apply_project_list(self, req, search_key, status, action_type,
                                            hospital=None, login_staff=None, staffs=None):
        """
        获取我负责的、我申请的项目列表
        """
        if action_type == 'my_performer':

            # 获取项目各状态条数
            status_count = ProjectPlan.objects.get_group_by_status(
                search_key=search_key, performer=req.user.get_profile()
            )
            result_projects = ProjectPlan.objects.get_my_performer_projects(
                hospital, login_staff, creators=staffs, project_title=search_key, status=status
            )
        elif action_type == 'apply':
            status_count = ProjectPlan.objects.get_group_by_status(
                search_key=search_key, creator=req.user.get_profile()
            )
            result_projects = ProjectPlan.objects.get_applied_projects(
                hospital, login_staff, performers=staffs, project_title=search_key, status=status
            )

        return self.get_projects_and_status_count_data(result_projects, status_count)

    def response_project_list(self, **result_data):
        status_count_data = dict(result_data.get('status_count'))
        if not status_count_data.get('SD'):
            status_count_data['SD'] = 0
        if not status_count_data.get('PE'):
            status_count_data['PE'] = 0
        if not status_count_data.get('DO'):
            status_count_data['DO'] = 0

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(
            result_data.get('result_projects'))
        response = self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer',
            results_name='projects'
        )
        response.data.update(
            self.get_project_status_count(**status_count_data)
        )
        return response

    def get_project_status_count(self, **data):
        """
        返回项目各状态条数数据结构，该结构添加到最终的json响应结果里
        :return: 返回数据形如:
            "project_status_count": {
                "project_pending_count": 17,    项目待启动数量
                "project_started_count": 0,     项目进行中数量
                "project_down_count": 0         项目完成数量
            }
        """
        projects_status_count = 'project_status_count'  # 项目数量块标示
        project_started_count = 'project_started_count'  # 进行中项目数量
        project_pending_count = 'project_pending_count'  # 待启动项目数量
        project_done_count = 'project_done_count'  # 已完成的项目数量
        return {
            projects_status_count: OrderedDict([
                (project_pending_count, data.get('PE')),
                (project_started_count, data.get('SD')),
                (project_done_count, data.get('DO'))
            ])
        }

    def get_projects_and_status_count_data(self, project, count):

        return {'result_projects': project,
                'status_count': count}


class ProjectPlanCreateView(BaseAPIView):
    """
    创建项目信息化项目申请（信息化硬件项目申请、信息化软件项目申请）
    """
    permission_classes = [HospitalStaffPermission, ]

    @check_id_list(["organ_id", "creator_id", "related_dept_id"])
    @check_params_not_null(['project_title', 'handing_type', 'pro_type'])
    def post(self, req):
        """
        创建项目申请（device_type:区分此项目属于信息化硬件申请还是信息化软件项目申请）
        device_type(
            hardware: 申请项目类型为信息化硬件项目申请
            software: 申请项目类型为信息化软件项目申请
        )
        医疗器械项目申请Example:
        {
            "organ_id": 20180606,
            "project_title": "政府要求采购项目",
            "handing_type": '自行办理'
            "device_type": 'HW'
            "purpose": "本次申请经科室共同研究决定, 响应政府号召",
            "creator_id": 20181001,
            "related_dept_id": 	10001001,
            "hardware_devices": [
                {
                    "name": "胎心仪",
                    "type_spec": "PE29-1389",
                    "num": 2,
                    "measure": "台",
                    "purpose": "用来测胎儿心电",
                    "planned_price": 15000.0
                },
                {
                    "name": "理疗仪",
                    "type_spec": "ST19-1399",
                    "num": 5,
                    "measure": "台",
                    "purpose": "心理科室需要",
                    "planned_price": 25000.0
                }
            ]
         }
         信息化项目申请Example:
         {
            'organ_id': 20180606,
            'project_title': '新建信息化项目申请项目',
            'handing_type': '自行办理'
            'device_type': 'SW'
            'purpose': '申请项目介绍'
            'software_devices':[
                {
                    'name': '易冉单点登录系统',
                    'purpose': '一次登录，解决多次重复登录其它应用',
                    'producer': '软件开发商'
                }
            ],
            "hardware_devices": [
                {
                    "name": "胎心仪",
                    "type_spec": "PE29-1389",
                    "num": 2,
                    "measure": "台",
                    "purpose": "用来测胎儿心电",
                    "planned_price": 15000.0
                },
                {
                    "name": "理疗仪",
                    "type_spec": "ST19-1399",
                    "num": 5,
                    "measure": "台",
                    "purpose": "心理科室需要",
                    "planned_price": 25000.0
                }
            ]
         }
        """
        objects = self.get_objects_or_404({
            "organ_id":         Hospital,
            "creator_id":       Staff,
            "related_dept_id":  Department
        })

        self.check_object_permissions(req, objects['organ_id'])

        if req.data.get('pro_type') not in dict(PROJECT_CATE_CHOICES).keys():
            return resp.form_err({'type_error': '不存在的操作类型'})

        form = ProjectPlanCreateForm(
            objects.get('creator_id'), objects.get('related_dept_id'),
            data=req.data
        )
        if not form.is_valid():
            return resp.form_err(form.errors)
        project = form.save()
        if not project:
            return resp.failed('项目申请提交异常')

        return resp.serialize_response(
            project, srl_cls_name='ChunkProjectPlanSerializer', results_name='project'
        )


class ProjectPlanView(BaseAPIView):
    """
    单个项目操作（任何权限都可对项目进行操作，此操作建立在该申请项目未分配负责人）
    """

    permission_classes = (
        IsHospitalAdmin, ProjectDispatcherPermission, HospitalStaffPermission
    )

    @check_id('organ_id')
    def get(self, req, project_id):     # 项目详情
        """
        需要项目管理员权限或者项目为提交者自己的项目
        """
        project = self.get_object_or_404(project_id, ProjectPlan)
        hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        self.check_object_any_permissions(req, hospital)

        project_queryset = ProjectPlan.objects.filter(id=project_id)
        project = ChunkProjectPlanSerializer.setup_eager_loading(project_queryset).first()
        return resp.serialize_response(
            project, results_name="project", srl_cls_name='ChunkProjectPlanSerializer'
        )

    @check_id('organ_id')
    @check_params_not_all_null(['project_title', 'purpose', 'handing_type',
                                'software_added_devices', 'software_updated_devices',
                                'hardware_added_devices', 'hardware_updated_devices'])
    def put(self, req, project_id):
        """
        修改项目.
        """

        hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        old_project = self.get_object_or_404(project_id, ProjectPlan)

        self.check_object_any_permissions(req, hospital)
        if old_project.project_cate == PRO_CATE_HARDWARE:
            if not old_project.is_unstarted():
                return resp.failed('项目已启动或已完成, 无法修改')

            form = ProjectPlanUpdateForm(old_project, data=req.data)
            if not form.is_valid():
                return resp.form_err(form.errors)
            new_project = form.save()
            if not new_project:
                return resp.failed('项目修改失败')

            new_project_queryset = ChunkProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)
            ).first()
            return resp.serialize_response(
                new_project_queryset, srl_cls_name='ChunkProjectPlanSerializer', results_name='project'
            )
        else:
            if not old_project.is_unstarted():
                return resp.failed('项目已启动或完成，无法修改')
            form = ProjectPlanUpdateForm(old_project, data=req.data)
            if not form.is_valid():
                return resp.form_err(form.errors)
            new_project = form.save()
            if not new_project:
                return resp.failed('项目修改失败')
            new_project_queryset = ChunkProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)
            ).first()
            return resp.serialize_response(
                new_project_queryset, srl_cls_name='ChunkProjectPlanSerializer', results_name='project'
            )

    def delete(self, req, project_id):
        """
        删除项目(已分配负责人的项目不能被删除)
        :param req:
        :param project_id: 申请项目ID
        """
        project = self.get_object_or_404(project_id, ProjectPlan)
        hospital = self.get_object_or_404(req.user.get_profile().organ.id, Hospital)
        self.check_object_any_permissions(req, hospital)

        if not project.performer:
            if project.deleted():
                return resp.ok('操作成功')
            return resp.failed('操作失败')
        return resp.failed('项目已被分配，无法删除')


class ProjectPlanDispatchView(BaseAPIView):
    """
    项目分配责任人(管理员或项目分配者才可分配负责人，分配默认流程，改变项目状态，项目直接进入默认流程的需求论证里程碑)
    """
    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission, )

    @check_id('performer_id')
    def put(self, req, project_id):
        project = self.get_object_or_404(project_id, ProjectPlan)
        staff = self.get_object_or_404(req.data.get('performer_id'), Staff,)

        # 检查当前操作者是否具有管理员和项目分配者权限
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        success = project.dispatch(staff)
        project_queryset = ProjectPlanSerializer.setup_eager_loading(ProjectPlan.objects.filter(id=project_id)).first()
        return resp.serialize_response(
            project_queryset,
            results_name="project",
            srl_cls_name='ProjectPlanSerializer'
        ) if success else resp.failed("操作失败")


class ProjectPlanRedispatchView(BaseAPIView):
    """
    重新分配项目负责人（不改变项目里程碑状态，只改变负责人信息）
    """
    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission,)

    @check_id('performer_id')
    def put(self, req, project_id):
        project = self.get_object_or_404(project_id, ProjectPlan)
        staff = self.get_object_or_404(req.data.get('performer_id'), Staff, )

        # 检查当前操作者是否具有管理员和项目分配者权限
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        success = project.redispatch(staff)
        project_queryset = ProjectPlanSerializer.setup_eager_loading(
            ProjectPlan.objects.filter(id=project_id)).first()
        return resp.serialize_response(
            project_queryset,
            results_name="project",
            srl_cls_name='ProjectPlanSerializer'
        ) if success else resp.failed("操作失败")


class ProjectPlanOverruleView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission,)

    def put(self, req, project_id):
        """
        项目负责人驳回项目
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)
        if project.status == PRO_STATUS_OVERRULE:
            return resp.failed('项目状态为驳回状态')
        operation_record_data = {
            'project': project_id,
            'reason': req.data.get('reason'),
            'operation': PRO_OPERATION_OVERRULE
        }
        if project.change_status(status=PRO_STATUS_OVERRULE, **operation_record_data):
            project_queryset = ProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)).first()
            return resp.serialize_response(project_queryset, results_name='project')
        else:
            return resp.failed("操作失败")


class ProjectPlanStartupView(BaseAPIView):
    """
    启动项目
    TODO: 权限后续需优化
    """
    permission_classes = (IsHospitalAdmin, HospitalStaffPermission, ProjectDispatcherPermission)

    @check_id_list(['flow_id',])
    @check_params_not_null(["expired_time"])
    def put(self, req, project_id):
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)
        if not req.user.get_profile().id == project.performer_id:
            return resp.failed("无操作权限")

        flow = self.get_object_or_404(req.data.get('flow_id'), ProjectFlow)
        data = {}
        if req.data.get('assistant_id'):
            data['assistant'] = self.get_object_or_404(req.data.get('assistant_id'), Staff)
        if not project.is_unstarted():
            return resp.failed("项目已启动或已完成，无需再启动")
        success = project.startup(
            flow=flow,
            expired_time=req.data.get('expired_time'),
            **data,
        )
        project_queryset = ProjectPlanSerializer.setup_eager_loading(ProjectPlan.objects.filter(id=project_id)).first()
        return resp.serialize_response(
            project_queryset, results_name="project", srl_cls_name='ProjectPlanSerializer'
        ) if success else resp.failed("操作失败")


class ProjectPlanChangeMilestoneView(BaseAPIView):
    """
    变更项目里程碑状态
    """

    permission_classes = (ProjectPerformerPermission, )

    @check_id_list(['milestone_id', ])
    @check_params_not_null(['done_sign', ])
    def post(self, req, project_id):
        project = self.get_object_or_404(project_id, ProjectPlan, use_cache=False)
        self.check_object_permissions(req, project)

        new_milestone = self.get_objects_or_404({'milestone_id': Milestone}, use_cache=False)['milestone_id']
        success, msg = project.change_milestone(new_milestone, done_sign=req.data.get('done_sign', FLOW_UNDONE).strip())
        if not success:
            return resp.failed(msg)

        return resp.serialize_response(
            project, results_name='project', srl_cls_name='ChunkProjectPlanSerializer'
        )


class ProjectDeviceCreateView(BaseAPIView):
    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def post(self, req, project_id):
        """ 添加设备 """
        project = self.get_object_or_404(project_id, ProjectPlan)
        if not project.is_unstarted():
            return resp.failed('项目已启动或已完成, 无法修改')

        form = OrderedDeviceCreateForm(project, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_device = form.save()
        return resp.serialize_response(new_device, results_name="device")


class ProjectSoftwareDeviceCreateView(BaseAPIView):
    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)


class ProjectDeviceView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def put(self, req, project_id, device_id):
        """ 修改设备信息 """

        project = self.get_object_or_404(project_id, ProjectPlan)
        if not project.is_unstarted():
            return resp.failed('项目已启动或已完成, 无法修改')

        device = self.get_object_or_404(device_id, OrderedDevice)
        form = OrderedDeviceUpdateForm(device, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        updated_device = form.save()
        return resp.serialize_response(updated_device, results_name="device")

    @check_params_not_null(['device_type'])
    def post(self, req, project_id, device_id):
        """
        删除申请项目中的相关硬件/软件设备信息（如果项目已在使用当中，则无法删除该设备）
        :param req:
        :param project_id: 被删除设备的项目ID
        :param device_id: 被删除设备的ID
        :return:
        """
        project = self.get_object_or_404(project_id, ProjectPlan)
        if not (req.user.get_profile() == project.creator):  # 若不是项目的提交者, 则检查是否为项目管理员
            self.check_object_any_permissions(req, project.creator.organ)

        if not project.is_unstarted():
            return resp.failed('项目已启动或已完成, 无法修改')

        if req.data.get('device_type') not in ["HW", "SW"]:
            return resp.failed('不存在的设备类型')

        if req.data.get('device_type') == "HW":
            device = self.get_object_or_404(device_id, OrderedDevice)
        else:
            device = self.get_object_or_404(device_id, SoftwareDevice)
        try:
            device.clear_cache()
            device.delete()
            return resp.ok("操作成功")
        except Exception as e:
            logs.exception(e)
            return resp.failed("操作失败")


class ProjectFlowChildMilestones(BaseAPIView):
    """
    获取项目流程某里程碑项的所有直接子里程碑项
    """

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req, project_id, flow_id, milestone_id):

        project = self.get_object_or_404(project_id, ProjectPlan)
        flow = self.get_object_or_404(flow_id, ProjectFlow)
        milestone = self.get_object_or_404(milestone_id, Milestone)
        attached_flow = project.attached_flow
        if flow.id != attached_flow.id or not attached_flow.contains(milestone):
            return resp.failed("参数数据异常")
        child_milestones = milestone.children()
        return resp.serialize_response(child_milestones, results_name='milestones', srl_cls_name='MilestoneSerializer')


class ProjectFlowCreateView(BaseAPIView):
    """
    创建项目流程对象
    """

    permission_classes = (IsHospitalAdmin, )

    @check_id('organ_id')
    @check_params_not_null(['flow_title', 'milestones'])
    def post(self, req):
        """

        参数Example:
        {
            "organ_id": 10001,
            "flow_title":       "项目标准流程",
            "milestones": [
                {
                    "title": "前期准备",
                    "index": 1
                },
                {
                    "title": "进入实施",
                    "index": 2
                }
            ]
        }
        """
        hosp = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        self.check_object_permissions(req, hosp)

        form = ProjectFlowCreateForm(hosp, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        flow = form.save()
        return resp.serialize_response(flow, results_name="flow") if flow else resp.failed("操作失败")


class ProjectFlowListView(BaseAPIView):

    def get(self, req):
        """ 返回流程列表 """
        pass


class ProjectFlowView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    def get(self, req, flow_id):
        """
        流程详情. 允许所有员工查看
        """
        pass

    @check_id('organ_id')
    @check_params_not_null(['flow_title', ])
    def put(self, req, flow_id):
        """
        修改流程名称及其他属性信息, 修改不包括添加/删除/修改流程内的里程碑项(已提取到单独的接口)
        仅允许管理员操作
        TODO： 添加修改限制条件
        """
        organ = self.get_object_or_404(req.data.get('organ_id'), Hospital)
        self.check_object_permissions(req, organ)

        flow = self.get_object_or_404(flow_id, ProjectFlow)
        form = ProjectFlowUpdateForm(flow, req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)

        new_flow = form.save()
        if not new_flow:
            return resp.failed('操作失败')
        return resp.serialize_response(new_flow, results_name='flow')

    def delete(self, req, flow_id):
        """
        删除流程. 仅允许管理员操作

        如果流程已经在使用，不能删除
        TODO： 添加删除限制条件
        """
        flow = self.get_object_or_404(flow_id, ProjectFlow)
        self.check_object_permissions(req, flow.organ)

        if flow.is_used():
            return resp.failed('流程已经在使用中，不能修改')
        flow.clear_cache()
        try:
            flow.delete()
        except Exception as e:
            logs.info(e)
            return resp.failed('操作失败')
        return resp.ok('操作成功')


class ProjectPlanDispatchedView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req):
        """
        获取已分配项目列表
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        dispatched_projects = ProjectPlan.objects.get_dispatched_projects(req.user.get_profile().organ)

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(dispatched_projects)

        return self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer',
            results_name='projects'
        )


class MilestoneCreateView(BaseAPIView):

    permission_classes = (IsHospitalAdmin,)

    def post(self, req, flow_id):
        """
        为指定流程添加里程碑项
        """
        pass


class MilestoneView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, )

    def put(self, req, flow_id, mid):
        """ 修改里程碑项 """
        pass

    def delete(self, req, flow_id, mid):
        """ 删除里程碑项 """
        pass
