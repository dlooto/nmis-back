# Generated by Django 2.0 on 2018-11-28 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hospitals', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('type', models.CharField(blank=True, choices=[('AN', '公告类消息'), ('RE', '提醒类消息'), ('ME', '系统类消息')], default='RE', max_length=10, verbose_name='办理方式')),
                ('content', models.TextField(blank=True, null=True, verbose_name='消息内容')),
            ],
            options={
                'verbose_name': 'A 消息记录',
                'verbose_name_plural': 'A 消息记录',
                'db_table': 'notices_notice',
            },
        ),
        migrations.CreateModel(
            name='UserNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('is_read', models.BooleanField(default=False, verbose_name='是否已读')),
                ('is_delete', models.BooleanField(default=False, verbose_name='是否已删除')),
                ('read_time', models.DateTimeField(null=True, verbose_name='消息读取时间')),
                ('delete_time', models.DateTimeField(null=True, verbose_name='消息删除时间')),
                ('notice', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, to='notices.Notice', verbose_name='')),
                ('staff', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='staff_notice', to='hospitals.Staff', verbose_name='')),
            ],
            options={
                'verbose_name': 'A 用户与消息关系',
                'verbose_name_plural': 'A 用户与消息关系',
                'db_table': 'notices_user_notice',
            },
        ),
        migrations.AlterUniqueTogether(
            name='usernotice',
            unique_together={('staff', 'notice')},
        ),
    ]
