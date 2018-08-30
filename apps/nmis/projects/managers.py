# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 

import logging

from django.db import transaction, DataError, models
from django_bulk_update import helper

from base.models import BaseManager
from nmis.devices.models import OrderedDevice, SoftwareDevice
from nmis.projects.consts import PRO_CATE_HARDWARE, PRO_CATE_SOFTWARE, PRO_STATUS_STARTED

logger = logging.getLogger(__name__)


class ProjectPlanManager(BaseManager):

    def create_project(self, hardware_devices=None, software_devices=None, **data):
        """
        创建项目项目(新建信息化硬件项目，新建信息化软件项目)

        :param hardware_devices: 硬件设备明细, 列表数据, 列表元素类型为dict
        :param software_devices: 软件设备明细, 列表数据, 列表元素类型为dict
        :param data: 字典型参数
        :return:
        """
        try:
            with transaction.atomic():
                project = self.model(**data)
                project.save()

                # 批量创建设备明细
                ordered_device_list = []
                if data.get('project_cate') == PRO_CATE_HARDWARE:
                    for device_data in hardware_devices:
                        ordered_device_list.append(
                            OrderedDevice(project=project, **device_data)
                        )
                    OrderedDevice.objects.bulk_create(ordered_device_list)

                else:
                    if hardware_devices:
                        for device_data in hardware_devices:
                            ordered_device_list.append(
                                OrderedDevice(project=project, **device_data)
                            )
                        OrderedDevice.objects.bulk_create(ordered_device_list)
                    if software_devices:
                        ordered_device_list = []
                        for device_data in software_devices:
                            ordered_device_list.append(
                                SoftwareDevice(project=project, **device_data)
                            )
                        SoftwareDevice.objects.bulk_create(ordered_device_list)
        except DataError as dex:
            logger.exception(dex)
            return None
        except Exception as e:
            logger.exception(e)
            return None
        return project

    # def get_allot_projects(self):
    #     return self.filter(performer=None)

    def get_undispatched_projects(self, dept_id_list, organ, project_title=None, creators=None):
        """
        按关键字(项目名/项目申请人)查询机构所有待分配的项目列表
        """
        from django.db.models import Q

        query_set = self.filter(related_dept__organ=organ, related_dept_id__in=dept_id_list, performer=None)
        if project_title or creators:
            query_set = query_set.filter(
                Q(title__contains=project_title) | Q(creator__in=creators)
            ).distinct()
        return query_set.order_by('-created_time')

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
        return query_set.order_by('-created_time')

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
        return query_set.order_by('-created_time')

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
        return query_set.order_by('-created_time')

    def get_dispatched_projects(self, organ):
        """
        获取已分配项目列表
        """
        query_set = self.filter(related_dept__organ=organ, status=PRO_STATUS_STARTED)

        return query_set.order_by('-created_time')

    def start_project(self):
        """
        TODO:
        """
        pass

    def update_project(self, old_project, **data):
        """
        TODO:
        :param old_project:
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

                if data.get('hardware_added_devices'):
                    # 批量添加新增的医疗器械设备明细
                    hardware_device_list = []
                    for device_data in data.get('hardware_added_devices'):
                        hardware_device_list.append(
                            OrderedDevice(project=old_project, **device_data)
                        )
                    OrderedDevice.objects.bulk_create(hardware_device_list)

                if data.get('hardware_updated_devices'):
                    # 批量修改医疗器械设备明细
                    hardware_updated_device_list = sorted(data.get('hardware_updated_devices'), key=lambda item: item['id'])
                    hardware_updated_id_list = [update_device['id'] for update_device in hardware_updated_device_list]

                    devices = OrderedDevice.objects.filter(pk__in=hardware_updated_id_list).order_by("id")
                    for i in range(len(devices)):
                        devices[i].name = hardware_updated_device_list[i].get('name')
                        devices[i].num = hardware_updated_device_list[i].get('num')
                        devices[i].planned_price = hardware_updated_device_list[i].get('planned_price')
                        devices[i].measure = hardware_updated_device_list[i].get('measure')
                        devices[i].purpose = hardware_updated_device_list[i].get('purpose')
                        devices[i].type_spec = hardware_updated_device_list[i].get('type_spec')
                    helper.bulk_update(devices)

                if old_project.project_cate == PRO_CATE_SOFTWARE:
                    if data.get('software_added_devices'):
                        # 批量添加新增的信息化设备明细
                        software_added_device_list = []
                        for device_data in data.get('software_added_devices'):
                            software_added_device_list.append(
                                SoftwareDevice(project=old_project, **device_data)
                            )
                        SoftwareDevice.objects.bulk_create(software_added_device_list)
                    if data.get('software_updated_devices'):
                        # 批量修改信息化设备
                        software_update_device_list = sorted(
                            data.get('software_updated_devices'), key=lambda item: item['id']
                        )
                        software_updated_id_list = [software['id'] for software in software_update_device_list]
                        software_old_device_list = SoftwareDevice.objects.filter(pk__in=software_updated_id_list).order_by('id')
                        for i in range(len(software_old_device_list)):
                            software_old_device_list[i].name = software_update_device_list[i].get('name')
                            software_old_device_list[i].purpose = software_update_device_list[i].get('purpose')
                        helper.bulk_update(software_old_device_list)
        except Exception as e:
            logger.exception(e)
            return None

        return new_project

    def get_group_by_status(self, search_key=None, status=None, creator=None, performer=None):
        """
        根据项目状态返回每个状态下项目数量(项目总览各状态条数，我申请的项目各状态条数，我负责的各状态条数)
        :return:
        """
        if status:
            return self.filter(status=status)\
                .values_list('status').annotate(models.Count('id'))
        if creator:
            return self.filter(creator=creator, title__contains=search_key)\
                .values_list('status').annotate(models.Count('id'))
        if performer:
            return self.filter(performer=performer, title__contains=search_key)\
                .values_list('status').annotate(models.Count('id'))
        return self.filter(title__contains=search_key).values_list('status').annotate(models.Count('id'))


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


class ProjectOperationRecordManager(BaseManager):

    def add_operation_records(self, **data):
        project_operation_record = self.model(**data)
        project_operation_record.save()
        project_operation_record.cache()
        return project_operation_record
