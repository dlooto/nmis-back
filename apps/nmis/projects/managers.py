# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging

from django.db import transaction

from base.models import BaseManager
from nmis.devices.models import OrderedDevice

logger = logging.getLogger(__name__)


class ProjectPlanManager(BaseManager):

    def create_project(self, ordered_devices, **data):
        """
        创建项目项目

        :param ordered_devices: 设备明细, 列表数据, 列表元素类型为dict
        :param data: 字典型参数
        :return:
        """
        try:
            with transaction.atomic():
                project = self.model(**data)
                project.save()

                # 批量创建设备明细
                ordered_device_list = []
                for device_data in ordered_devices:
                    ordered_device_list.append(
                        OrderedDevice(project=project, **device_data)
                    )
                OrderedDevice.objects.bulk_create(ordered_device_list)
        except Exception as e:
            logger.exception(e)
            return None

        return project

    # def get_allot_projects(self):
    #     return self.filter(performer=None)

    def get_undispatched_projects(self, organ):
        """ 返回机构待分配(负责人)的项目列表 """
        return self.filter(related_dept__organ=organ, performer=None)

    def get_by_search_key(self, organ, project_title=None, performers=None, **fields):
        """
        按关键字(项目名/项目负责人名)查询机构拥有的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ, **fields)
        if project_title or performers:
            query_set = query_set.filter(Q(title__contains=project_title) | Q(performer__in=performers)).distinct()
        return query_set

    def get_applied_projects(self, organ, creator):
        """
        返回项目申请者申请的项目列表
        :param organ: 项目申请者所有机构
        :param creator: 项目申请者staff object
        :return:
        """
        return self.filter(related_dept__organ=organ, creator=creator)

    def start_project(self,):
        """
        TODO:
        """
        pass


class ProjectFlowManager(BaseManager):

    def create_flow(self, milestones, **data):
        """
        创建项目流程
        :param milestones:
        :param data:
        :return:
        """
        from .models import Milestone

        try:
            with transaction.atomic():
                flow = self.model(**data)
                flow.save()

                milestone_list = []
                for ms in milestones:
                    milestone_list.append(Milestone(flow=flow, **ms))
                Milestone.objects.bulk_create(milestone_list)
        except Exception as e:
            logger.exception(e)
            return None

        return flow