# Generated by Django 2.0 on 2018-10-30 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitals', '0010_auto_20181029_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='cate',
            field=models.CharField(choices=[('CNM', '普通角色类')], default='CNM', max_length=4, verbose_name='类别'),
        ),
    ]
