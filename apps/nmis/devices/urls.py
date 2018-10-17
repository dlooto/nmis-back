# coding=utf-8
#
# Created by gonghuaiqian, on 2018-10-16
#

"""

"""

import logging

from django.urls import path

from . import views

logger = logging.getLogger(__name__)


urlpatterns = [
    path('repair_orders/create',                    views.RepairOrderCreateView.as_view(), ),
    path('repair_orders/<int:order_id>',            views.RepairOrderView.as_view(), ),
    path('repair_orders',                          views.RepairOrderListView.as_view(), ),

]
