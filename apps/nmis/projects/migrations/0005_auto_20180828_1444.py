# Generated by Django 2.0 on 2018-08-28 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20180828_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectplan',
            name='pre_amount',
            field=models.FloatField(blank=True, null=True, verbose_name='项目预估总价'),
        ),
    ]
