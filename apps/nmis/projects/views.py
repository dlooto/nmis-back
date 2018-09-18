# coding=utf-8
#
# Created by junn, on 2018/6/7
#

#
import logging
import os
import settings

from django.db import transaction

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
    ProjectFlowUpdateForm, UploadFileForm, PurchaseContractCreateForm,
    SingleUploadFileForm,
    ProjectDocumentBulkCreateForm)
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone, ProjectDocument, \
    ProjectMilestoneState, SupplierSelectionPlan, Supplier
from nmis.projects.permissions import ProjectPerformerPermission, \
    ProjectAssistantPermission
from nmis.projects.serializers import ChunkProjectPlanSerializer, ProjectPlanSerializer, \
    get_project_status_count

from nmis.hospitals.consts import (
    GROUP_CATE_PROJECT_APPROVER,
    GROUP_CATE_NORMAL_STAFF,
    ARCHIVE)
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
    PRO_OPERATION_OVERRULE,
    PRO_STATUS_PAUSE,
    PRO_OPERATION_PAUSE,
    PROJECT_DOCUMENT_DIR, PROJECT_PURCHASE_METHOD_CHOICES, PROJECT_DOCUMENT_CATE_CHOICES,
    PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN, PRO_DOC_CATE_OTHERS)
from utils.files import upload_file, remove, is_file_exist

logger = logging.getLogger(__name__)


class ProjectPlanListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req):
        """
        获取项目总览列表
        参数列表：
            type:       string    项目类型
            organ_id:   int       当前医院ID
            pro_status: string    项目状态（PE：未启动，SD：已启动，DO：已完成，OR：已驳回，PA：已挂起）
            search_key: string    项目名称/项目申请人关键字
        """
        # 检查管理员权限,允许管理员/项目分配者操作

        self.check_object_any_permissions(req, req.user.get_profile().organ)

        status = req.GET.get('pro_status', '').strip()
        # 项目状态校验
        if status:
            if status not in dict(PROJECT_STATUS_CHOICES):
                return resp.form_err({'err_status': '项目状态异常'})
        search_key = req.GET.get('search_key', '').strip()

        # 根据关键字查询staffs集合
        staffs = None
        if search_key:
            staffs = Staff.objects.get_by_name(req.user.get_profile().organ, search_key)

        # 获取项目各状态条数
        status_count = ProjectPlan.objects.get_group_by_status(search_key=search_key)

        total_projects = ProjectPlan.objects.get_by_search_key(
            req.user.get_profile().organ, project_title=search_key, performers=staffs, status=status
        )

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(total_projects)
        response = self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects'
        )
        response.data.update(get_project_status_count(**dict(status_count)))

        return response


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

            if not old_project.is_unstarted() or old_project.is_paused():
                return resp.failed('项目已启动或已完成或被挂起, 无法修改')

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
            if not old_project.is_unstarted or old_project.is_paused():
                return resp.failed('项目已启动或完成或被挂起，无法修改')
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

        if project.status in (PRO_STATUS_STARTED, PRO_STATUS_DONE, PRO_STATUS_PAUSE, PRO_STATUS_OVERRULE):
            return resp.failed('%s %s %s' % ('项目状态:', project.status, ',无法分配'))

        success, result = project.dispatch(staff)
        if success:
            success, result = project.change_project_milestone_state(result)
            if not success:
                return resp.failed(result)
        else:
            return resp.failed('操作失败')
        project_queryset = ProjectPlanSerializer.setup_eager_loading(ProjectPlan.objects.filter(id=project_id)).first()
        return resp.serialize_response(
            project_queryset,
            results_name="project",
            srl_cls_name='ProjectPlanSerializer'
        )


class ProjectPlanRedispatchView(BaseAPIView):
    """
    重新分配项目负责人（不改变项目里程碑状态，只改变负责人信息）
    """
    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission,)

    @check_id('performer_id')
    def put(self, req, project_id):
        # 检查当前操作者是否具有管理员和项目分配者权限
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        project = self.get_object_or_404(project_id, ProjectPlan)
        staff = self.get_object_or_404(req.data.get('performer_id'), Staff, )

        if project.status in (PRO_STATUS_DONE, PRO_STATUS_PAUSE, PRO_STATUS_OVERRULE):
            return resp.failed('%s %s %s' % ('项目状态:', project.status, ',无法分配'))

        success = project.redispatch(staff)
        if success:
            project_queryset = ProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)).first()
            return resp.serialize_response(
                project_queryset,
                results_name="project",
                srl_cls_name='ProjectPlanSerializer'
            )
        return resp.failed("操作失败")


class ProjectPlanOverruleView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission,)

    @check_params_not_null(['reason'])
    def put(self, req, project_id):
        """
        项目分配者驳回项目
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)

        operation_record_data = {
            'project': project_id,
            'reason': req.data.get('reason', '').strip(),
            'operation': PRO_OPERATION_OVERRULE
        }
        if project.change_status(status=PRO_STATUS_OVERRULE, **operation_record_data):

            project_queryset = ProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)).first()
            return resp.serialize_response(project_queryset, results_name='project')
        else:
            return resp.failed("操作失败")


class ProjectPlanPauseView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission, HospitalStaffPermission)

    @check_params_not_null(['reason'])
    def put(self, req, project_id):
        """
        项目负责人挂起项目
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)

        operation_record_data = {
            'project': project_id,
            'reason': req.data.get('reason', '').strip(),
            'operation': PRO_OPERATION_PAUSE
        }
        if project.change_status(status=PRO_STATUS_PAUSE, **operation_record_data):
            project_queryset = ProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)).first()
            return resp.serialize_response(project_queryset, results_name='project')
        else:
            return resp.failed("操作失败")


class ProjectPlanCancelPauseView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission, HospitalStaffPermission)

    def put(self, req, project_id):
        """
        项目负责人取消挂起的项目
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        project = self.get_object_or_404(project_id, ProjectPlan)
        if project.status == PRO_STATUS_DONE:
            return resp.failed('项目已完成，不能进行该操作')
        if project.cancel_pause():
            project_queryset = ProjectPlanSerializer.setup_eager_loading(
                ProjectPlan.objects.filter(id=project_id)).first()
            return resp.serialize_response(project_queryset, results_name='project')
        else:
            return resp.failed('操作失败')


class ProjectPlanDispatchAssistantView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @check_id('assistant_id')
    def put(self, req, project_id):
        """
        项目负责人分配项目协助办理人
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)

        staff = self.get_object_or_404(req.data.get('assistant_id'), Staff)

        if project.dispatched_assistant(staff):
            return resp.ok("操作成功")

        return resp.ok('操作失败')


class ProjectPlanAssistedListView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req):
        """
        获取我协助的项目列表
        参数列表：
            pro_status: string    项目状态（SD：已启动，DO：已完成，PA：已挂起）
            search_key: string    项目名称/项目申请人关键字
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        search_key = req.GET.get('search_key', '').strip()
        status = req.GET.get('pro_status', '').strip()
        # 项目状态校验
        if status:
            if status not in dict(PROJECT_STATUS_CHOICES):
                return resp.form_err({'err_status': '项目状态异常'})
        performer_staffs = None

        if search_key:
            performer_staffs = Staff.objects.get_by_name(req.user.get_profile().organ, search_key)

        query_set = ProjectPlan.objects.get_my_assistant_projects(
            organ=req.user.get_profile().organ, assistant=req.user.get_profile(),
            performer=performer_staffs, project_title=search_key, status=status)

        # 获取项目各个状态的条数
        status_count = ProjectPlan.objects.get_group_by_status(
            search_key=search_key, assistant=req.user.get_profile())

        # 调用serializer预加载
        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(query_set)

        response = self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer',
            results_name='projects'
        )
        # response更新各项目状态条数
        response.data.update(get_project_status_count(**dict(status_count)))
        return response


class ProjectPlanPerformedListView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req):
        """
        获取我负责的项目列表
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        search_key = req.GET.get('search_key', '').strip()
        status = req.GET.get('pro_status', '').strip()
        if status:
            if status not in dict(PROJECT_STATUS_CHOICES):
                return resp.form_err({'status_err': '项目状态异常'})

        creators_staffs = None
        if search_key:
            creators_staffs = Staff.objects.get_by_name(req.user.get_profile().organ, search_key)

        # 获取项目各状态条数
        status_count = ProjectPlan.objects.get_group_by_status(
            search_key=search_key, performer=req.user.get_profile()
        )
        performed_projects = ProjectPlan.objects.get_my_performer_projects(
            req.user.get_profile().organ, req.user.get_profile(),
            creators=creators_staffs, project_title=search_key,
            status=status
        )

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(performed_projects)

        response = self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects'
        )

        response.data.update(get_project_status_count(**dict(status_count)))

        return response


class ProjectPlanAppliedListView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req):
        """
        获取我申请的项目列表
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        search_key = req.GET.get('search_key', '').strip()
        status = req.GET.get('pro_status', '').strip()

        performer_staffs = None
        if search_key:
            performer_staffs = Staff.objects.get_by_name(req.user.get_profile().organ, search_key)
        if status:
            if status not in dict(PROJECT_STATUS_CHOICES):
                return resp.form_err({'status_err': '项目状态异常'})

        status_count = ProjectPlan.objects.get_group_by_status(
            search_key=search_key, creator=req.user.get_profile()
        )
        applied_projects = ProjectPlan.objects.get_applied_projects(
            req.user.get_profile().organ, req.user.get_profile(),
            performers=performer_staffs, project_title=search_key,
            status=status
        )

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(applied_projects)
        response = self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects'
        )
        response.data.update(get_project_status_count(**dict(status_count)))
        return response


class ProjectPlanStartupView(BaseAPIView):
    """
    启动项目
    TODO: 权限后续需优化
    """
    permission_classes = (IsHospitalAdmin, HospitalStaffPermission, ProjectDispatcherPermission)

    @check_id_list(['flow_id', ])
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


class ProjectPlanChangeMilestoneStateView(BaseAPIView):
    """
    变更当前项目里程碑的状态:
    完结当前项目里程碑，同时点亮下一个里程碑(如果下一个里程碑有子里程碑，同时点亮下一个里程碑的第一个子里程碑）
    """
    # permission_classes = (ProjectPerformerPermission, )
    @check_id('project_milestone_state_id')
    def post(self, req, project_id, ):

        project = self.get_object_or_404(project_id, ProjectPlan)
        self.check_object_permissions(req, project)
        curr_milestone_state = self.get_object_or_404(req.data.get('project_milestone_state_id'), ProjectMilestoneState)
        success, msg = project.change_project_milestone_state(curr_milestone_state)
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
            logger.exception(e)
            return resp.failed("操作失败")


class ProjectChildMilestoneStatesView(BaseAPIView):
    """
    获取项目流程某里程碑项的所有直接子里程碑项
    """

    # permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req, project_id, project_milestone_state_id):

        project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if pro_milestone_state.milestone.flow != project.attached_flow or not project.contains_project_milestone_state(pro_milestone_state):
            return resp.failed("操作失败，数据异常")
        child_milestones = pro_milestone_state.milestone.children()
        child_milestone_states = ProjectMilestoneState.objects.filter(project=project, milestone__in=child_milestones)

        return resp.serialize_response(child_milestone_states, results_name='project_milestone_states', srl_cls_name='ChunkProjectMilestoneStateSerializer')


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
            logger.info(e)
            return resp.failed('操作失败')
        return resp.ok('操作成功')


class FlowChildMilestonesView(BaseAPIView):
    """
    获取流程某里程碑项的所有直接子里程碑项
    """

    # permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req, flow_id, mid):

        flow = self.get_object_or_404(flow_id, ProjectFlow)
        milestone = self.get_object_or_404(mid, Milestone)
        if milestone.flow != flow or not flow.contains(milestone):
            return resp.failed("参数数据异常")
        child_milestones = milestone.children()
        return resp.serialize_response(child_milestones, results_name='milestones', srl_cls_name='MilestoneSerializer')


class ProjectPlanDispatchedListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req):
        """
        获取已分配项目列表
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        # 获取权限组ID
        group_id_list = [group.id for group in req.user.get_permissions()]
        # 获取权限域中部门ID
        dept_id_list = self.get_user_role_dept_domains(req, group_id_list)

        dispatched_projects = ProjectPlan.objects.get_dispatched_projects(
            dept_id_list, req.user.get_profile().organ
        )

        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(dispatched_projects)

        return self.get_pages(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer',
            results_name='projects'
        )


class ProjectPlanUndispatchedListView(BaseAPIView):

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    def get(self, req):
        """
        获取项目待分配列表
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        # 获取权限组ID
        group_id_list = [group.id for group in req.user.get_permissions()]
        # 获取权限域中部门ID
        dept_id_list = self.get_user_role_dept_domains(req, group_id_list)

        undispatched_projects = ProjectPlan.objects.get_undispatched_projects(
            dept_id_list, req.user.get_profile().organ
        )
        result_projects = ChunkProjectPlanSerializer.setup_eager_loading(undispatched_projects)

        return self.get_pages(result_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects')


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


class ProjectMilestoneStateResearchInfoCreateView(BaseAPIView):
    # permission_classes = (IsHospitalAdmin, ProjectPerformerPermission, ProjectAssistantPermission)

    """
    项目负责人/项目协助人保存/修改[调研]里程碑下的信息
    """
    @check_params_not_all_null(['files', 'summary'])
    def post(self, req, project_id, project_milestone_state_id, ):
        project = self.get_object_or_404(project_id, ProjectPlan)
        milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not milestone_state.milestone.title == '调研':
            return resp.failed('操作失败，当前里程碑不是【调研】里程碑')
        # if stone_state.is_finished():
        #     return resp.failed('操作失败，当前里程碑已完结')

        if project.performer == req.user.get_profile():
            if req.data.get('summary') and req.data.get('summary').strip():
                milestone_state.summary = req.data.get('summary')

        if req.data.get('files'):
            form = ProjectDocumentBulkCreateForm(req.data.get('files'))
            if not form.is_valid():
                return resp.form_err(form.errors)
            doc_list = form.save()
            if not doc_list:
                return resp.serialize_response(milestone_state, results_name='project_milestone_state', srl_cls_name='ChunkProjectMilestoneStateSerializer')
            doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
            if not milestone_state.save_doc_list(doc_ids_str):
                return resp.failed('保存失败')

        return resp.serialize_response(milestone_state, results_name='project_milestone_state', srl_cls_name='ChunkProjectMilestoneStateSerializer')


class ProjectMilestoneStateResearchInfoView(BaseAPIView):
    """
    查看[调研]里程碑下的信息
    """
    def get(self, req, project_id, project_milestone_state_id):

        project = self.get_object_or_404(project_id, ProjectPlan)
        stone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not stone_state.milestone.title == '调研':
            return resp.failed('操作失败，当前里程碑不是【调研】里程碑')
        return resp.serialize_response(stone_state, results_name='project_milestone_state', srl_cls_name='ChunkProjectMilestoneStateSerializer')


class ProjectMilestoneStatePlanGatheredCreateView(BaseAPIView):
    """保存[方案收集]里程碑下的信息"""

    @check_params_not_all_null(['plan_list', 'summary'])
    @transaction.atomic()
    def post(self, req, project_id, project_milestone_state_id):
        project = self.get_object_or_404(project_id, ProjectPlan)
        stone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not stone_state.milestone.title == '方案收集':
            return resp.failed('操作失败，当前里程碑不是【方案收集】里程碑')
        # if stone_state.is_finished():
        #     return resp.failed("操作失败，当前里程碑已完结")

        if project.performer == req.user.get_profile():
            if req.data.get('summary'):
                stone_state.summary = req.data.get('summary')
        plan_list = req.data.get("plan_list")
        if plan_list:
            try:
                with transaction.atomic():
                    for item in plan_list:
                        supplier = item.get('supplier')
                        total_amount = item.get('total_amount')
                        remark = item.get('remark')
                        files = item.get('files')
                        # 创建供应商
                        supplier, created = Supplier.objects.update_or_create(name=supplier)
                        supplier.cache()
                        # 创建供应商选择方案
                        plan, created = SupplierSelectionPlan.objects.update_or_create(project_milestone_state=stone_state, supplier=supplier)
                        if total_amount:
                            plan.total_amount = total_amount
                        if remark:
                            plan.remark = remark
                        plan.save()
                        plan.cache()
                        if not files:
                            continue
                        form = ProjectDocumentBulkCreateForm(item.get('files'))
                        if not form.is_valid():
                            return resp.form_err(form.errors)
                        doc_list = form.save()
                        if not doc_list:
                            continue
                        doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
                        if not plan.doc_list:
                            plan.doc_list = doc_ids_str
                        else:
                            plan.doc_list = '%s%s%s' % (self.doc_list, ',', doc_ids_str)
                        plan.save()
                        plan.cache()
            except Exception as e:
                logger.exception(e)
                return resp.failed('操作失败')
        return resp.serialize_response(stone_state, results_name='project_milestone_state', srl_cls_name='ProjectMilestoneStateWithSupplierSelectionPlanSerializer')


class ProjectMilestoneStatePlanGatheredView(BaseAPIView):
    """
    查询[方案收集]里程碑下的信息
    """
    def get(self, req, project_id, project_milestone_state_id):
        project = self.get_object_or_404(project_id, ProjectPlan)
        stone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not stone_state.milestone.title == '方案收集':
            return resp.failed('操作失败，当前里程碑不是【方案收集】里程碑')
        return resp.serialize_response(stone_state, results_name='project_milestone_state', srl_cls_name='ProjectMilestoneStateWithSupplierSelectionPlanSerializer')


class ProjectMilestoneStatePlanGatheredFileView(BaseAPIView):

    @transaction.atomic()
    def delete(self, req, project_id, project_milestone_state_id, plan_id, doc_id):
        """
        删除【方案收集】里程碑下的方案附件或其他资料附件(单个)
        :param req:
        :param project_id:
        :param project_milestone_state_id:
        :return:
        """
        project = self.get_object_or_404(project_id, ProjectPlan)
        milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not milestone_state.milestone.title == '方案收集':
            return resp.failed('操作失败，当前里程碑不是【方案收集】里程碑')
        # if milestone_state.is_finished():
        #     return resp.failed("操作失败，当前里程碑已完结")
        plan = self.get_object_or_404(plan_id, SupplierSelectionPlan)
        doc = self.get_object_or_404(doc_id, ProjectDocument)
        try:
            path = os.path.join(settings.MEDIA_ROOT, doc.path)
            if is_file_exist(path):
                if remove(path):
                    doc_ids_str = plan.doc_list.split(",")
                    if str(doc_id) in doc_ids_str:
                        doc_ids_str.remove(str(doc_id))
                    plan.doc_list = ",".join(doc_ids_str)
                    plan.save()
                    plan.cache()
                    doc.delete()
                    resp.ok("操作成功")
            else:
                doc_ids_str = plan.doc_list.split(",")
                if str(doc_id) in doc_ids_str:
                    doc_ids_str.remove(str(doc_id))
                plan.doc_list = ",".join(doc_ids_str)
                plan.save()
                plan.cache()
                doc.delete()
                resp.ok("操作成功")
        except Exception as e:
            logger.exception(e)
            resp.failed("操作失败")


class ProjectMilestoneStateSupplierPlanView(BaseAPIView):

    @transaction.atomic()
    def delete(self, req, project_id, project_milestone_state_id):
        """
        删除【方案收集】里程碑下的供应商方案
        :param req:
        :param project_id:
        :param project_milestone_state_id:
        :return:
        """


class ProjectMilestoneStatePlanArgumentCreateView(BaseAPIView):
    """
    保存[方案论证]里程碑下的信息
    """

    @check_id('selected_plan_id')
    @transaction.atomic()
    def post(self, req, project_id, project_milestone_state_id):
        """
        圈定选择的供应商待选方案
        :param req: Request对象
        :param project_id: 当前项目id
        :param project_milestone_state_id: 当前里程碑信息
        :return: 返回当前项目里程碑下信息，包括供应商选择方案，文档资料附件等
        """
        project = self.get_object_or_404(project_id, ProjectPlan)
        milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not milestone_state.milestone.title == '方案论证':
            return resp.failed('操作失败，当前里程碑不是【方案论证】里程碑')
        # if stone_state.is_finished():
        #     return resp.failed("操作失败，当前里程碑已完结")

        selected_plan = self.get_object_or_404(req.data.get('selected_plan_id'), SupplierSelectionPlan)
        selected_plan.selected = True
        selected_plan.save()
        selected_plan.cache()

        if project.performer == req.user.get_profile():
            if req.data.get('summary'):
                milestone_state.summary = req.data.get('summary')
                milestone_state.save()
                milestone_state.cache()
        if req.data.get("files"):
            form = ProjectDocumentBulkCreateForm(req.data.get('files'))
            if not form.is_valid():
                return resp.form_err(form.errors)
            doc_list = form.save()
            if not doc_list:
                pass
            doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
            if not milestone_state.save_doc_list(doc_ids_str):
                return resp.failed('操作异常，请重新保存')
        plans = SupplierSelectionPlan.objects.filter(project_milestone_state=selected_plan.project_milestone_state)
        milestone_state.supplier_selection_plans = plans
        return resp.serialize_response(
            milestone_state, results_name='project_milestone_state',
            srl_cls_name='ProjectMilestoneStateWithSupplierSelectionPlanSelectedSerializer'
        )


class ProjectMilestoneStatePlanArgumentView(BaseAPIView):
    """
    查看[方案论证]里程碑下的信息
    """
    @check_id('supplier_plan_related_milestone_state_id')
    def get(self, req, project_id, project_milestone_state_id):
        project = self.get_object_or_404(project_id, ProjectPlan)
        current_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)
        if not current_milestone_state.milestone.title == '方案论证':
            return resp.failed('操作失败，当前里程碑不是【方案论证】里程碑')
        supplier_plan_related_milestone_state_id = req.GET.get('supplier_plan_related_milestone_state_id')
        supplier_plan_related_milestone_state = self.get_object_or_404(supplier_plan_related_milestone_state_id, ProjectMilestoneState)

        plans = SupplierSelectionPlan.objects.filter(project_milestone_state=supplier_plan_related_milestone_state)
        current_milestone_state.supplier_selection_plans = plans

        return resp.serialize_response(
            current_milestone_state,
            results_name='project_milestone_state',
            srl_cls_name='ProjectMilestoneStateWithSupplierSelectionPlanSelectedSerializer'
        )


class MilestoneRecordPurchaseCreateView(BaseAPIView):

    permission_classes = (HospitalStaffPermission,)

    @transaction.atomic
    def post(self, req, project_id, project_milestone_state_id):
        """
        确定采购方式子里程碑记录操作（包括确定采购的方式，保存采购方式决策论证类附件，保存说明等操作）
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_states = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState, use_cache=False)

        purchase_method = req.data.get('purchase_method', '').strip()

        if not project.purchase_method:
            if not purchase_method:
                return resp.failed('请选择采购方式')
        if purchase_method:
            if purchase_method not in dict(PROJECT_PURCHASE_METHOD_CHOICES):
                return resp.form_err({'purchase_method_err': '采购方式类型错误'})
            else:
                success = project.determining_purchase_method(purchase_method)
                if not success:
                    return resp.failed('保存失败')

        if req.data.get('files'):
            form = ProjectDocumentBulkCreateForm(req.data.get('files'))
            if not form.is_valid():
                return resp.form_err(form.errors)
            doc_list = form.save()
            if not doc_list:
                return resp.serialize_response(
                    pro_milestone_states,
                    srl_cls_name='ChunkProjectMilestoneStateSerializer',
                    results_name='project_milestone_state')
            doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
            if not pro_milestone_states.save_doc_list(doc_ids_str):
                return resp.failed('保存失败')

        if req.user.get_profile() == project.performer:
            if req.data.get('summary', '').strip():
                if pro_milestone_states.update_summary(req.data.get('summary', '').strip()):
                    return resp.serialize_response(
                        pro_milestone_states,
                        srl_cls_name='ChunkProjectMilestoneStateSerializer',
                        results_name='project_milestone_state')
        if req.user.get_profile() == project.assistant:
            return resp.serialize_response(
                pro_milestone_states,
                srl_cls_name='ChunkProjectMilestoneStateSerializer',
                results_name='project_milestone_state')

        return resp.failed('保存失败')


class MilestoneRecordPurchaseView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req, project_milestone_state_id):
        """
        获取确定采购方案信息(包括:采购方式、决策论证资料、说明等)
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        # project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState, use_cache=False)
        logger.info(pro_milestone_state.doc_list)
        # milestone_record = ProjectMilestoneState.objects.get_milestone_state(project)

        return resp.serialize_response(
            pro_milestone_state,
            srl_cls_name='ChunkProjectMilestoneStateSerializer',
            results_name='project_milestone_state'
        )


class MilestoneStartUpPurchaseCreateView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @transaction.atomic
    def post(self, req, project_id, project_milestone_state_id):
        """
        启动采购里程碑中保存操作(保存资料文档url地址，项目里程碑中的说明、文档集合)
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)

        if not req.data.get('files') and not req.data.get('summary'):
            return resp.failed('请输入保存内容')

        if req.data.get('files'):
            form = ProjectDocumentBulkCreateForm(req.data.get('files'))

            if not form.is_valid():
                return resp.form_err(form.errors)

            doc_list = form.save()

            if not doc_list:
                return resp.failed('保存失败')

            doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
            if not pro_milestone_state.save_doc_list(doc_ids_str):
                return resp.failed('保存失败')

        if req.user.get_profile() == project.performer:
            if req.data.get('summary', '').strip():
                if pro_milestone_state.update_summary(req.data.get('summary', '').strip()):
                    return resp.serialize_response(
                        pro_milestone_state,
                        srl_cls_name='ChunkProjectMilestoneStateSerializer',
                        results_name='project_milestone_state')
        if req.user.get_profile() == project.assistant:
            return resp.serialize_response(
                pro_milestone_state,
                srl_cls_name='ChunkProjectMilestoneStateSerializer',
                results_name='project_milestone_state')

        return resp.failed('保存失败')


class MilestoneStartUpPurchaseView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def get(self, req, project_milestone_state_id):
        """
        获取启动采购中附件和说明相关信息
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        # project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)

        return resp.serialize_response(
            pro_milestone_state,
            srl_cls_name='ChunkProjectMilestoneStateSerializer',
            results_name='project_milestone_state')


class MilestonePurchaseContractCreateView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    @transaction.atomic
    @check_params_not_null(['contract_no', 'title', 'signed_date', 'buyer_contact',
                            'seller_contact', 'seller', 'seller_tel', 'total_amount',
                            'delivery_date', 'contract_device'])
    def post(self, req, project_id, project_milestone_state_id):
        """
        合同管理里程碑操作（保存合同信息、合同中设备信息、附件地址、说明信息）
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        project = self.get_object_or_404(project_id, ProjectPlan)
        pro_milestone_state = self.get_object_or_404(project_milestone_state_id, ProjectMilestoneState)

        logger.info(req.data.get('contract_device'))

        purchase_form = PurchaseContractCreateForm(req.data)
        if not purchase_form.is_valid():
            return resp.form_err(purchase_form.errors)

        if not req.FILES and not req.data:
            return resp.failed('请输入内容')
        form = UploadFileForm(req, project_id)
        if not form.is_valid():
            return resp.form_err(form.errors)
        result_data, success = form.save()
        if not success:
            return resp.failed('文件上传失败')
        # 上传文件成功后，保存资料文档记录，并添加文档添加到ProjectMilestoneRecord中
        # doc_list = ProjectDocument.objects.batch_save_upload_project_doc(result_data)
        # doc_ids_str = ','.join('%s' % doc.id for doc in doc_list)
        # record, is_created = ProjectMilestoneState.objects.update_or_create(
        #     project=project, milestone=milestone)
        #
        # if is_created:
        #     record.doc_list = doc_ids_str
        # else:
        #     if doc_ids_str:
        #         if record.doc_list:
        #             record.doc_list = '%s%s%s' % (record.doc_list, ',', doc_ids_str)
        #         else:
        #             record.doc_list = doc_ids_str
        #
        # if req.user.get_profile().id == project.performer.id:
        #
        #     summary = req.data.get('summary', '').strip()
        #     if summary:
        #         record.summary = summary
        # record.save()
        # record.cache()
        # return resp.serialize_response(record, results_name='milestone_record')
        return resp.ok('保存成功')


class UploadFileView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, )

    def post(self, req, project_id):
        """
        流程中每个子里程碑中的文件上传
        :return: 保存至服务器，返回保存路径
        """
        self.check_object_permissions(req, req.user.get_profile().organ)

        project = self.get_object_or_404(project_id, ProjectPlan)

        form = SingleUploadFileForm(req, project_id)

        if not form.is_valid():
            return resp.failed(form.errors)
        result, file_name, success = form.save()
        if not success:
            return resp.failed(result)
        file_url = {
            'file_url': result.get(file_name)
        }
        return resp.ok(data=file_url)


class DeleteFileView(BaseAPIView):

    permission_classes = (HospitalStaffPermission,)

    @check_id('project_milestone_state_id')
    @transaction.atomic
    def post(self, req, doc_id):
        """
        单个文件的删除（删除project_document的记录，更新project_milestone_states中doc_list记录，从服务器中删除文件）
        :return:
        """
        self.check_object_permissions(req, req.user.get_profile().organ)
        project_document = self.get_object_or_404(doc_id, ProjectDocument)

        # 获取项目里程碑state
        project_milestone_state = ProjectMilestoneState.objects.get_pro_milestone_states_by_id(
            req.data.get('project_milestone_state_id')
        )
        if project_milestone_state:
            doc_id_str = project_milestone_state.doc_list.split(',')

            if str(doc_id) in doc_id_str:
                doc_id_str.remove(str(doc_id))
            if project_milestone_state.update_doc_list(",".join(doc_id_str)):
                path = os.path.join(settings.MEDIA_ROOT, project_document.path)
                if remove(path):
                    if project_document.deleted():
                        return resp.ok('删除成功')

        return resp.failed('系统找不到指定的路径')
