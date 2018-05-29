# coding=utf-8
#
# Created by junn, on 2018-5-29
#

"""

"""

import logging

from django.conf.urls import url

from . import views

logs = logging.getLogger(__name__)


urlpatterns = [
    url(r"^(\d+)$",         views.HospitalHomeView.as_view()),
]