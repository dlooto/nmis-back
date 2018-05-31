# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 

import logging

from base.models import BaseModel

logs = logging.getLogger(__name__)


class PurchaseRequest(BaseModel):
    """
    一次采购申请
    """

    class Meta:
        verbose_name = u'采购申请'
        verbose_name_plural = u'采购申请'
        db_table = 'projects_purchase_request'


class PurchasePlan(BaseModel):
    """
    一次采购计划
    """

    class Meta:
        verbose_name = u'采购计划'
        verbose_name_plural = u'采购计划'
        db_table = 'projects_purchase_plan'


class Contract(BaseModel):
    """
    采购合同
    """

    class Meta:
        verbose_name = u'采购合同'
        verbose_name_plural = u'采购合同'
        db_table = 'projects_contract'


class Supplier(BaseModel):
    """
    供应商
    """

    class Meta:
        verbose_name = u'供应商'
        verbose_name_plural = u'供应商'
        db_table = 'projects_supplier'