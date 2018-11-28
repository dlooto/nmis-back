from django.contrib import admin

from .models import Notice

# Register your models here.


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'content', 'created_time')


admin.site.register(Notice, NoticeAdmin)