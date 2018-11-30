# Generated by Django 2.0 on 2018-11-28 14:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0002_auto_20181128_1448'),
        ('devices', '0002_auto_20181119_1506'),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalDeviceCate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='分类编码')),
                ('title', models.CharField(max_length=128, verbose_name='分类名称')),
                ('level_code', models.CharField(max_length=20, verbose_name='同级编码')),
                ('level', models.SmallIntegerField(default=0, verbose_name='分类层级')),
                ('example', models.TextField(blank=True, max_length=2048, null=True, verbose_name='品名举例')),
                ('mgt_cate', models.SmallIntegerField(choices=[(1, 'Ⅱ'), (2, 'Ⅲ'), (3, 'Ⅲ')], null=True, verbose_name='管理类别')),
                ('modified_time', models.DateTimeField(auto_now=True, null=True, verbose_name='修改时间')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_medical_device_cates', to='hospitals.Staff', verbose_name='创建人')),
                ('modifier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='modified_medical_device_cates', to='hospitals.Staff', verbose_name='修改人')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cate_children', to='devices.MedicalDeviceCate', verbose_name='父级分类')),
            ],
            options={
                'verbose_name': ' 医疗器械分类目录',
                'verbose_name_plural': ' 医疗器械分类目录',
                'db_table': 'devices_medical_device_cate',
                'permissions': (('view_medical_device_cate', 'can view medical device cate'),),
            },
        ),
        migrations.RemoveField(
            model_name='medicaldevicesix8cate',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='medicaldevicesix8cate',
            name='modifier',
        ),
        migrations.RemoveField(
            model_name='medicaldevicesix8cate',
            name='parent',
        ),
        migrations.AlterField(
            model_name='assertdevice',
            name='medical_device_cate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='related_assert_device', to='devices.MedicalDeviceCate', verbose_name='医疗器械分类'),
        ),
        migrations.DeleteModel(
            name='MedicalDeviceSix8Cate',
        ),
    ]