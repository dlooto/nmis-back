#coding=utf-8
#
# Created by junn, on 16/11/29
#

"""

"""

import logging

from django.conf.urls import url, include
from django.views.generic import TemplateView
import views

logs = logging.getLogger(__name__)


urlpatterns = [
    # url(r"^$",      TemplateView.as_view(template_name='users/signup_success_email.html')),
    url(r"^show_messages$", TemplateView.as_view(template_name='tests/test.html')),
    url(r'^current_user$',      views.UserView.as_view(), ),

]