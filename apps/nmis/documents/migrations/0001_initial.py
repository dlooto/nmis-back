# Generated by Django 2.0 on 2018-11-19 15:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=128, verbose_name='文件名称')),
                ('path', models.CharField(max_length=255, verbose_name='文件存放路径')),
                ('cate', models.CharField(default='UNKNOWN', max_length=32, verbose_name='文件类别')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建人')),
            ],
            options={
                'verbose_name': '文件资料',
                'verbose_name_plural': '文件资料',
                'db_table': 'documents_file',
                'permissions': (('view_file', 'can view file'),),
            },
        ),
    ]
