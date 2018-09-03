# Generated by Django 2.0 on 2018-08-29 18:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_merge_20180829_1038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='milestone',
            old_name='parent_milestone',
            new_name='parent',
        ),
        migrations.AlterField(
            model_name='projectflow',
            name='default_flow',
            field=models.BooleanField(default=False, verbose_name='是否为默认流程'),
        ),
    ]