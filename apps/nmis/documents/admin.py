# coding=utf-8
#
# Created by gong, on 2018-10-16
#

"""

"""

import logging

from django.contrib import admin

from nmis.documents.models import File

logger = logging.getLogger(__name__)


class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'cate', "path", 'uuid_name'
    )


admin.site.register(File, FileAdmin)





