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
        try:
            with transaction.atomic():
                project = self.model(**data)
                project.save()

                # 批量创建设备明细
                ordered_device_list = []
                for device_data in ordered_devices:
                    ordered_device_list.append(
                        OrderedDevice(**device_data)
                    )
                OrderedDevice.objects.bulk_create(ordered_device_list)
        except Exception as e:
            logger.exception(e)
            return None

        return project


class ProjectFlowManager(BaseManager):
    pass