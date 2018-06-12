# coding=utf-8
#
# Created by junn, on 2018/6/7
#

# 

import logging

from rest_framework.permissions import AllowAny

from base import resp
from base.common.decorators import check_id, check_id_list, check_params_not_null
from base.common.permissions import OrPermission
from base.views import BaseAPIView
from nmis.hospitals.models import Hospital, Staff, Department
from nmis.hospitals.permissions import HospitalStaffPermission,  \
    IsHospitalAdmin, ProjectApproverPermission
from nmis.projects.forms import ProjectPlanCreateForm
from nmis.projects.models import ProjectPlan

logs = logging.getLogger(__name__)


class ProjectPlanListView(BaseAPIView):
    """
    项目列表操作
    """
    def get(self, req):
        pass


class ProjectPlanCreateView(BaseAPIView):
    """

    """
    permission_classes = [HospitalStaffPermission, ]

    @check_id_list(["hospital_id", "creator_id", "related_dept_id"])
    @check_params_not_null(['project_title', 'ordered_devices'])
    def post(self, req):
        """
        创建项目申请, 项目申请提交后进入未分配(待启动)状态.

        Example:
        {
            "hospital_id": 20180606,
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
            "hospital_id":      Hospital,
            "creator_id":       Staff,
            "related_dept_id":  Department
        })

        self.check_object_permissions(req, objects['hospital_id'])

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

    permission_classes = (IsHospitalAdmin, ProjectApproverPermission)

    @check_id('hospital_id')
    def get(self, req, project_id):     # 项目详情
        project = ProjectPlan.objects.get_by_id(project_id)
        hospital = self.get_objects_or_404({'hospital_id': Hospital})['hospital_id']
        if not (req.user.get_profile() == project.creator):  # 若不是项目的提交者, 则检查是否为项目管理员
            self.check_object_any_permissions(req, hospital)

        return resp.serialize_response(
            project, results_name="project", srl_cls_name='ChunkProjectPlanSerializer'
        )

    def put(self, req, project_id):     # 修改项目
        pass

    def delete(self, req, project_id):  # 删除项目
        raise NotImplementedError()


