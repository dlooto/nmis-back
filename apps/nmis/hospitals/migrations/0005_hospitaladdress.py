# Generated by Django 2.0 on 2018-10-16 13:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0004_merge_20180828_1337'),
    ]

    operations = [
        migrations.CreateModel(
            name='HospitalAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('title', models.CharField(max_length=128, verbose_name='名称')),
                ('type', models.CharField(choices=[('BD', '楼'), ('RM', '房间')], max_length=3, verbose_name='类型')),
                ('parent_path', models.CharField(default='', max_length=1024, verbose_name='父地址路径')),
                ('level', models.SmallIntegerField(verbose_name='层级')),
                ('sort', models.SmallIntegerField(verbose_name='排序')),
                ('disabled', models.BooleanField(default=False, verbose_name='是否禁用')),
                ('desc', models.CharField(blank=True, max_length=256, null=True, verbose_name='描述')),
                ('dept', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hospitals.Department', verbose_name='所属科室')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='hospitals.HospitalAddress', verbose_name='父级地址')),
            ],
            options={
                'verbose_name': '医院内部地址',
                'verbose_name_plural': '医院内部地址',
                'db_table': 'hospitals_hospital_area',
            },
        ),
    ]
