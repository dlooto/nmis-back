# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from django.db import models

from base.models import BaseModel

logs = logging.getLogger(__name__)


class Device(BaseModel):
    """
    一般设备/器械基础模型
    """
    name = models.CharField('设备名称', max_length=30)
    cate = models.CharField('设备类型', max_length=10, null=True, blank=True)
    producer = models.CharField('设备生产者', max_length=30, null=True, blank=True)

    class Meta:
        abstract = True


class OrderedDevice(Device):
    """
    申购的医疗设备, 一般作为申请项目里的硬件设备明细条目
    """
    project = models.ForeignKey(
        'projects.ProjectPlan', verbose_name='所属项目', related_name='ordered_devices', on_delete=models.CASCADE, null=True, blank=True
    )
    planned_price = models.FloatField('预算单价', default=0.00)
    real_price = models.FloatField('实际单价', default=0.00, null=True, blank=True)
    num = models.IntegerField('预购数量', default=1)
    measure = models.CharField('度量/单位', max_length=5, null=True, blank=True)
    type_spec = models.CharField('规格/型号', max_length=20, null=True, blank=True)
    purpose = models.CharField('用途', max_length=20, null=True, blank=True, default='')

    class Meta:
        verbose_name = u'申购的硬件设备'
        verbose_name_plural = u'申购的硬件设备'
        db_table = 'devices_ordered_device'

    VALID_ATTRS = [
        'name', 'cate', 'producer', "num", "planned_price", "measure",
        "type_spec", "purpose"
    ]

    def __str__(self):
        return self.name


class SoftwareDevice(Device):
    """
    申购的软件设备，一般作为申请项目里的软件设备条目明细
    """
    project = models.ForeignKey(
        'projects.ProjectPlan', verbose_name='所属项目', related_name='software_devices',
        on_delete=models.CASCADE, null=True, blank=True
    )
    purpose = models.CharField('用途', max_length=20, null=True, blank=True, default='')

    real_price = models.FloatField('实际单价', default=0.00, null=True, blank=True)
    planned_price = models.FloatField('预算单价', default=0.00)

    class Meta:
        verbose_name = '申购的软件设备'
        verbose_name_plural = verbose_name
        db_table = 'devices_software_device'

    VALID_ATTRS = [
        'name', 'cate', 'purpose'
    ]

    def __str__(self):
        return self.name

# class MedicalDevice(Device):
#     """
#     作为资产的医疗设备
#     """
#     medical_cate = models.CharField('医疗分类', max_length=3, default='')
#     license = models.ForeignKey()
#
#     class Meta:
#         verbose_name = u'医疗设备'
#         verbose_name_plural = u'医疗设备'
#         db_table = 'devices_medical_device'

