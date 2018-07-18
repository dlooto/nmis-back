# Generated by Django 2.0 on 2018-07-17 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20180704_1440'),
        ('devices', '0002_auto_20180608_1814'),
    ]

    operations = [
        migrations.CreateModel(
            name='SoftwareDevice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=30, verbose_name='设备名称')),
                ('cate', models.CharField(blank=True, max_length=10, null=True, verbose_name='设备类型')),
                ('producer', models.CharField(blank=True, max_length=30, null=True, verbose_name='设备生产者')),
                ('purpose', models.CharField(blank=True, default='', max_length=20, null=True, verbose_name='用途')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='projects.ProjectPlan', verbose_name='所属项目')),
            ],
            options={
                'db_table': 'devices_software_device',
            },
        ),
    ]
