# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging

from django.db import transaction, DataError
from django_bulk_update import helper

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
        except DataError as dex:
            logger.exception(dex)
            return None
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
        按关键字(项目名/项目负责人名)查询机构所有的项目列表
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

    def get_applied_projects(self, organ, staff, performers=None, project_title=None, status=None):
        """
        按关键字:(项目名/项目负责人)查询机构所有我的申请项目列表
        :param organ: 项目申请者所有机构
        :param staff: 当前登录系统用户
        :param performers: 项目负责人Staff集合
        :param project_title: 项目名称
        :param status 项目状态
        """
        query_set = self.filter(related_dept__organ=organ, creator=staff)
        if status:
            query_set = query_set.filter(status=status)
        if performers or project_title:
            from django.db.models import Q
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(performer__in=performers)
            ).distinct()
        return query_set

    def get_my_performer_projects(self, organ, staff, creators=None, project_title=None, status=None):
        """
        按关键字:(项目名/项目申请人)查询机构所有我负责的项目列表
        :param organ:
        :param staff: 当前登录系统用户
        :param project_title: 项目名称
        :param creators 项目申请人Staff集合
        :param status 项目状态
        :param
        """
        query_set = self.filter(related_dept__organ=organ, performer=staff)
        if status:
            query_set = query_set.filter(status=status)
        if project_title or creators:
            from django.db.models import Q
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(creator__in=creators)
            ).distinct()
        return query_set

    def start_project(self,):
        """
        TODO:
        """
        pass

    def update_project(self, old_project, **data):
        """
        TODO:
        :param old_project:
        :param update_devices: 变更的设备明细, 列表数据, 列表元素类型为dict
        :param added_devices: 新添加的设备明细, 列表数据, 列表元素类型为dict
        :return:
        """

        try:
            with transaction.atomic():
                pro_base_data = {}
                if data.get('title'):
                    pro_base_data['title'] = data.get('title')
                if data.get('handing_type'):
                    pro_base_data['handing_type'] = data.get('handing_type')
                if data.get('purpose'):
                    pro_base_data['purpose'] = data.get('purpose')
                if pro_base_data:
                    new_project = old_project.update(pro_base_data)

                if data.get('added_devices'):
                    # 批量添加设备明细
                    ordered_device_list = []
                    for device_data in data.get('added_devices'):
                        ordered_device_list.append(
                            OrderedDevice(project=old_project, **device_data)
                        )
                    OrderedDevice.objects.bulk_create(ordered_device_list)
                if data.get('updated_devices'):
                    # 批量修改设备明细
                    updated_devices = sorted(data.get('updated_devices'), key=lambda item: item['id'])
                    updated_device_ids = [update_device['id'] for update_device in updated_devices]

                    devices = OrderedDevice.objects.filter(pk__in=updated_device_ids).order_by("id")
                    for i in range(len(devices)):
                        devices[i].name = updated_devices[i].get('name')
                        devices[i].num = updated_devices[i].get('num')
                        devices[i].planned_price = updated_devices[i].get('planned_price')
                        devices[i].measure = updated_devices[i].get('measure')
                        devices[i].purpose = updated_devices[i].get('purpose')
                        devices[i].type_spec = updated_devices[i].get('type_spec')
                    helper.bulk_update(devices)
        except Exception as e:
            logger.exception(e)
            return None

        return new_project


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