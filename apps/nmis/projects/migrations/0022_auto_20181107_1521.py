# Generated by Django 2.0 on 2018-11-07 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0021_auto_20181107_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmilestonestate',
            name='modified_time',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='最近一次修改时间'),
        ),
    ]