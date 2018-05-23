# coding=utf-8
#
# Created by junn, on 17/1/7
#

"""

"""

import logging

logs = logging.getLogger(__name__)

from django.conf.urls import url

import views


urlpatterns = [
    # 刷新渠道职位类别缓存
    # url(r'^flush_data$',  views.FlushDataView.as_view(), ),

]