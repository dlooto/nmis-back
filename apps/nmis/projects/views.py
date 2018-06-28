# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from base import resp
from base.common.decorators import (
    check_id, check_id_list, check_params_not_null, check_params_not_all_null
)
from base.views import BaseAPIView

from nmis.devices.models import OrderedDevice
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
    ProjectPlanListForm,
    ProjectFlowUpdateForm)
from nmis.projects.models import ProjectPlan, ProjectFlow, Milestone
from nmis.projects.permissions import ProjectPerformerPermission

logs = logging.getLogger(__name__)


class ProjectPlanListView(BaseAPIView):
    """
    项目列表操作
    """

    permission_classes = (HospitalStaffPermission, )

    @check_params_not_null(['organ_id', 'type'])
    def get(self, req):
        """
        获取项目列表，包括：我的项目列表（待筛选）、待分配项目列表
        """
        hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        self.check_object_permissions(req, req.user.get_profile().organ)  # 检查操作者权限

        action_type = req.GET.get("type")
        if action_type not in ('undispatch', 'my_projects', 'apply'):
            return resp.form_err({"type": "不存在的操作类型"})

        # 获取所有待分配的项目列表
        if action_type == 'undispatch':
            result_projects = ProjectPlan.objects.get_undispatched_projects(hospital)

        elif action_type == 'my_projects':  # 我申请的项目/我负责的项目
            """
            我的项目列表，带筛选
            参数列表：
                organ_id	int		当前医院ID
                pro_status	string  项目状态（PE：未启动，SD：已启动，DO：已完成）,为none查看全部
                pro_title_leader	string		项目名称/项目负责人
                creator_id	int		申请人ID（此ID为当前登录用户ID），筛选我申请的项目
                performer_id int	项目负责人ID（此ID为当前登录用户ID），筛选我负责的项目
                current_stone_id    里程碑id
            """

            form = ProjectPlanListForm(req, hospital)
            if not form.is_valid():
                return resp.form_err(form.errors)
            result_projects = form.my_projects()

        # 获取我申请的项目列表
        else:
            result_projects = ProjectPlan.objects.get_applied_projects(
                hospital, req.user.get_profile()
            )

        return resp.serialize_response(
            result_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects'
        )


class ProjectPlanCreateView(BaseAPIView):
    """

    """
    permission_classes = [HospitalStaffPermission, ]

    @check_id_list(["organ_id", "creator_id", "related_dept_id"])
    @check_params_not_null(['project_title', 'ordered_devices'])
    def post(self, req):
        """
        创建项目申请, 项目申请提交后进入未分配(待启动)状态.

        Example:
        {
            "organ_id": 20180606,
            "project_title": "政府要求采购项目",
            "purpose": "本次申请经科室共同研究决定, 响应政府号召",
            "creator_id": 20181001,
            "related_dept_id": 	10001001,
            "ordered_devices": [
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

        form = ProjectPlanCreateForm(
            objects['creator_id'], objects['related_dept_id'],
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
    单个项目操作
    """

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    @check_id('organ_id')
    def get(self, req, project_id):     # 项目详情
        """
        需要项目管理员权限或者项目为提交者自己的项目
        """
        project = ProjectPlan.objects.get_by_id(project_id)
        hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        if not (req.user.get_profile() == project.creator):  # 若不是项目的提交者, 则检查是否为项目管理员
            self.check_object_any_permissions(req, hospital)

        return resp.serialize_response(
            project, results_name="project", srl_cls_name='ChunkProjectPlanSerializer'
        )

    @check_id('organ_id')
    @check_params_not_all_null(['project_title', 'purpose'])
    def put(self, req, project_id):
        """
        修改项目. 该接口仅可以修改项目本身的属性, 若修改设备明细, 需要调用其他接口对设备逐个进行修改.
        """

        hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
        old_project = ProjectPlan.objects.get_by_id(project_id)
        if not (req.user.get_profile() == old_project.creator):  # 若不是项目的提交者, 则检查是否为项目管理员
            self.check_object_any_permissions(req, hospital)

        if not old_project.is_unstarted():
            return resp.failed('项目已启动或已完成, 无法修改')

        form = ProjectPlanUpdateForm(old_project, data=req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        new_project = form.save()
        if not new_project:
            return resp.failed('项目修改失败')

        return resp.serialize_response(new_project, srl_cls_name='ChunkProjectPlanSerializer',
                                       results_name='project')

    def delete(self, req, project_id):  # 删除项目
        raise NotImplementedError()


class ProjectPlanDispatchView(BaseAPIView):
    """
    项目分配责任人
    """

    permission_classes = (IsHospitalAdmin, ProjectDispatcherPermission)

    @check_id_list(['performer_id', 'flow_id'])
    @check_params_not_null(['expired_time'])
    def post(self, req, project_id):
        self.check_object_permissions(req, req.user.get_profile().organ)  # 检查操作者权限

        project = self.get_object_or_404(project_id, ProjectPlan)
        objects = self.get_objects_or_404({'performer_id': Staff, 'flow_id': ProjectFlow})
        success = project.dispatch(
            objects.get('performer_id'), flow=objects.get('flow_id'), expired_time=req.data.get('expired_time')
        )
        return resp.serialize_response(project, results_name="project") if success else resp.failed("操作失败")


class ProjectPlanChangeMilestoneView(BaseAPIView):
    """
    变更项目里程碑状态
    """

    permission_classes = (ProjectPerformerPermission, )

    @check_id_list(['milestone_id', ])
    def post(self, req, project_id):
        project = self.get_object_or_404(project_id, ProjectPlan, use_cache=False)
        self.check_object_permissions(req, project)

        new_milestone = self.get_objects_or_404({'milestone_id': Milestone}, use_cache=False)['milestone_id']
        success, msg = project.change_milestone(new_milestone)
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

    def delete(self, req, project_id, device_id):
        """ 删除存在的设备 """

        project = self.get_object_or_404(project_id, ProjectPlan)
        if not (req.user.get_profile() == project.creator):  # 若不是项目的提交者, 则检查是否为项目管理员
            self.check_object_any_permissions(req, project.creator.organ)

        if not project.is_unstarted():
            return resp.failed('项目已启动或已完成, 无法修改')

        device = self.get_object_or_404(device_id, OrderedDevice)
        try:
            device.delete()
            return resp.ok("操作成功")
        except Exception as e:
            logs.exception(e)
            return resp.failed("操作失败")


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
    @check_params_not_null(['flow_title',])
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


# class MyProjectListView(BaseAPIView):
#     permission_classes = (IsHospitalAdmin, )
#
#     @check_id('organ_id')
#     def get(self, req):
#         """
#         我的项目列表，带筛选
#         参数列表：
#             organ_id	int		当前医院ID
#             upper_expired_date	string		截止时间2（2018-06-01）
#             lower_expired_date	string		截止时间1（2018-06-19）
#             pro_status	string		项目状态（PE：未启动，SD：已启动，DO：已完成）,为none查看全部
#             pro_title_leader	string		项目名称/项目负责人
#             creator_id	int		申请人ID（此ID为当前登录用户ID），筛选我申请的项目
#             performer_id int	项目负责人ID（此ID为当前登录用户ID），筛选我负责的项目
#
#         """
#         hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
#         self.check_object_permissions(req, hospital)
#         form = ProjectPlanListForm(req, hospital)
#         if not form.is_valid():
#             return resp.form_err(form.errors)
#         return resp.serialize_response(
#             form.my_projects_plan(), srl_cls_name='ChunkProjectPlanSerializer',
#             results_name='projects'
#         )
#
#
# class AllotProjectListView(BaseAPIView):
#     permission_classes = (IsHospitalAdmin, )
#
#     @check_id('organ_id')
#     def get(self, req):
#         """
#         获取所有待分配的项目列表
#         """
#         hospital = self.get_objects_or_404({'organ_id': Hospital})['organ_id']
#         self.check_object_permissions(req, hospital)
#
#         undispatched_projects = ProjectPlan.objects.get_undispatched_projects(hospital)
#         return resp.serialize_response(
#             undispatched_projects, srl_cls_name='ChunkProjectPlanSerializer', results_name='projects'
#         )





