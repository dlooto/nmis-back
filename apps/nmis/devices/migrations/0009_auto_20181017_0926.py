# Generated by Django 2.0 on 2018-10-17 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0008_auto_20181016_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faulttype',
            name='title',
            field=models.CharField(max_length=32, verbose_name='故障类型名称'),
        ),
        migrations.AlterField(
            model_name='medicaldevicesix8cate',
            name='code',
            field=models.CharField(max_length=16, unique=True, verbose_name='分类编号'),
        ),
        migrations.AlterField(
            model_name='medicaldevicesix8cate',
            name='example',
            field=models.TextField(blank=True, max_length=2048, null=True, verbose_name='品名举例'),
        ),
    ]
