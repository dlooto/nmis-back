# coding=utf-8
#
# Created by junn, on 17/1/30
#

# 

from django.contrib.auth import get_user_model

# 默认起始业务ID设置

USER_ID_AUTO_START = 20161225       # 用户id自增起始值

superuser_email = 'admin@nmis.com'
superuser_password = 'xxxxxx'

# 该方法在migration中被使用
def create_superuser(apps, schema_editor):
    try:
        get_user_model().objects.create_superuser(
            superuser_email, superuser_password,
            username='admin'
        )
    except Exception as e:
        print('Create superuser failed when migration')
        print(e)


# id自增从设定的值开始
USERS_MIGRATION_INIT_SQL = [("alter table users_user AUTO_INCREMENT=%s;", [USER_ID_AUTO_START, ])]
