# coding=utf-8
#
# Created by junn, on 2018/5/29
#

# 医疗机构, 科室, 人员/医生等管理


from django.apps import AppConfig


class HospitalsAppConfig(AppConfig):
    name = 'nmis.hospitals'
    verbose_name = "医疗机构管理"

default_app_config = 'nmis.hospitals.HospitalsAppConfig'
