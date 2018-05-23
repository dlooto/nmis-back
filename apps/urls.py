# coding=utf-8

import settings

from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.conf.urls import include, url

admin.autodiscover()

urlpatterns = [
    url(r"^$",              TemplateView.as_view(template_name='index.html')),
    url(r'^admin/',         include(admin.site.urls)),

    # Web
    # url(r'^users/', include('users.urls')),
]

if settings.DEBUG:
    # Used in debug mode for handling user-uploaded files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # For html page testing
    urlpatterns += [
        url(r'^tests/', include('runtests.urls')),
    ]


