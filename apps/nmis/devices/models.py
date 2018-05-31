# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from base.models import BaseModel

logs = logging.getLogger(__name__)


class Device(BaseModel):
    """
    一般设备/器械
    """

    class Meta:
        abstract = True

# class MedicalDevice(Device):
#     """
#     医疗设备
#     """
#
#     class Meta:
#         verbose_name = u'医疗设备'
#         verbose_name_plural = u'医疗设备'
#         db_table = 'devices_medical_device'