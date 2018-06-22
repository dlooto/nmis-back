# coding=utf-8
#
# Created by junn, on 2018/6/13
#

# 测试中使用的基础数据及工具类

import logging

from nmis.projects.models import ProjectPlan

logs = logging.getLogger(__name__)


ORDERED_DEVICES = [
    {
        "name": "胎心仪",
        "type_spec": "PE29-1389",
        "num": 2,
        "measure": "台",
        "purpose": "用来测胎儿心电",
        "planned_price": 15000.0
    },
    {
        "name": "理疗仪",
        "type_spec": "ST19-1399",
        "num": 5,
        "measure": "台",
        "purpose": "心理科室需要",
        "planned_price": 25000.0
    }
]


class ProjectPlanMixin(object):
    """
    项目管理基础工具类
    """

    def create_project(self, creator, dept, title="设备采购", ordered_devices=ORDERED_DEVICES):
        """
        :param creator:  项目创建者, staff object
        :param dept: 申请科室
        """
        project_data = {
            'title': title,
            'purpose': "设备老旧换新",
            'creator': creator,
            'related_dept': dept,
        }
        return ProjectPlan.objects.create_project(ordered_devices, **project_data)