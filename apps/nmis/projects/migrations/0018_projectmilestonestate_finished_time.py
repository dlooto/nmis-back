# Generated by Django 2.0 on 2018-09-18 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_auto_20180913_1249'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmilestonestate',
            name='finished_time',
            field=models.DateTimeField(blank=True, default=None, null=True, verbose_name='项目里程碑完结时间'),
        ),
    ]