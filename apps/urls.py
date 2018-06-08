# coding=utf-8

import settings

from django.contrib import admin
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.urls import include, path

admin.autodiscover()

urlpatterns = [
    path("",              TemplateView.as_view(template_name='index.html')),
    path('admin/',        admin.site.urls),

    # API
    path('api/v1/users/',       include('users.urls')),
    path('api/v1/projects/',    include('nmis.projects.urls')),
]

if settings.DEBUG:
    # Used in debug mode for handling user-uploaded files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


