# Generated by Django 2.0 on 2018-11-30 10:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20181128_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assertdevice',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_assert_devices', to='hospitals.Staff', verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='assertdevice',
            name='performer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='performed_assert_devices', to='hospitals.Staff', verbose_name='资产负责人'),
        ),
        migrations.AlterField(
            model_name='assertdevice',
            name='responsible_dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='responsible_assert_devices', to='hospitals.Department', verbose_name='负责科室'),
        ),
        migrations.AlterField(
            model_name='assertdevice',
            name='storage_place',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='storage_assert_devices', to='hospitals.HospitalAddress', verbose_name='存放地点'),
        ),
        migrations.AlterField(
            model_name='assertdevice',
            name='use_dept',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='used_assert_devices', to='hospitals.Department', verbose_name='使用科室'),
        ),
    ]
