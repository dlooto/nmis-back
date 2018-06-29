# coding=utf-8
#
# Created by junn, on 17/1/30
#

# 


# id起始值规则说明
"""
user_id起始值:       10010001 (admin_user_id=10010000)
hospital_id起始值:   20040001
department_id起始值: 30030001
staff_id起始值:      40040001
project_id起始值:    50050001
"""

from django.contrib.auth import get_user_model

USER_ID_AUTO_START = 10010000       # 用户id自增起始值, admin_user_id值
PROJECT_ID_AUTO_START = 50050001    # 项目id自增起始值

superuser_email = 'admin@nmis.com'
superuser_password = 'Admin123'

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
SET_USER_START_ID = [("alter table users_user AUTO_INCREMENT=%s;", [USER_ID_AUTO_START, ])]
SET_PROJECT_START_ID = [("alter table projects_project_plan AUTO_INCREMENT=%s;", [PROJECT_ID_AUTO_START, ])]