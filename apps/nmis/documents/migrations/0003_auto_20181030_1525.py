# Generated by Django 2.0 on 2018-10-30 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_auto_20181019_2214'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='file',
            options={'permissions': (('view_file', 'can view file'),), 'verbose_name': '文件资料', 'verbose_name_plural': '文件资料'},
        ),
    ]