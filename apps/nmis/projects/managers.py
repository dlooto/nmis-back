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

    def get_undispatched_projects(self, organ, project_title=None, creators=None):
        """
        按关键字(项目名/项目申请人)查询机构所有待分配的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ, performer=None)
        if project_title or creators:
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(creator__in=creators)
            ).distinct()
        return query_set

    def get_by_search_key(self, organ, project_title=None, performers=None, status=None):
        """
        按关键字(项目名/项目负责人名)查询机构拥有的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ)
        if status:
            query_set = query_set.filter(status=status)
        if project_title or performers:
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(performer__in=performers)
            ).distinct()
        return query_set

    def get_applied_projects(self, organ, creator, project_title=None, status=None):
        """
        按关键字:(项目名)查询机构所有我的申请项目列表
        :param organ: 项目申请者所有机构
        :param creator: 项目申请者staff object
        :return:
        """
        query_set = self.filter(related_dept__organ=organ, creator=creator)
        if status:
            query_set = query_set.filter(status=status)
        if project_title:
            query_set = query_set.filter(title__contains=project_title)
        return query_set

    def get_my_performer_projects(self, organ, performer, project_title=None, status=None):
        """
        按关键字:(项目名)查询机构所有我负责的项目列表
        :param organ:
        :param performer: 项目负责人
        :param project_title: 项目名称关键字
        :param fields:
        :return:
        """
        query_set = self.filter(related_dept__organ=organ, performer=performer)
        if status:
            query_set = query_set.filter(status=status)
        if project_title:
            query_set = query_set.filter(title__contains=project_title)
        return query_set

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