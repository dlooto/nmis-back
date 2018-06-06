# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 医疗机构模块常量配置

import logging

logs = logging.getLogger(__name__)


# 医疗机构分类等级
HOSP_GRADE_3A = '3a'  # 3级甲等
HOSP_GRADE_3B = '3b'
HOSP_GRADE_3C = '3c'
HOSP_GRADE_2A = '2a'
HOSP_GRADE_2B = '2b'
HOSP_GRADE_2C = '2c'

HOSP_GRADE_CHOICES = (
    (HOSP_GRADE_3A, '三级甲等'),
    (HOSP_GRADE_3B, '三级乙等'),
    (HOSP_GRADE_3C, '三级丙等'),
    (HOSP_GRADE_2A, '二级甲等'),
    (HOSP_GRADE_2B, '二级乙等'),
    (HOSP_GRADE_2C, '二级丙等'),
)


# 科室/部门属性, 类别
DPT_ATTRI_MEDICAL = 'ME'
DPT_ATTRI_SUPPORT = 'SU'
DPT_ATTRI_OFFICE = 'OF'

DPT_ATTRI_CHOICES = (
    (DPT_ATTRI_MEDICAL, '医技'),
    (DPT_ATTRI_SUPPORT, '后勤'),
    (DPT_ATTRI_OFFICE,  '行政'),
)


# 医生职称
DOCTOR_CHIEF = 'CF'
DOCTOR_VICE_CHIEF = 'VCF'
DOCTOR_ATTEND = 'AT'
DOCTOR_RESIDENT = 'RE'

DOCTOR_TITLE_CHOICES = (
    (DOCTOR_CHIEF,      '主任医生'),
    (DOCTOR_VICE_CHIEF, '副主任医生'),
    (DOCTOR_ATTEND,     '主治医生'),
    (DOCTOR_RESIDENT,   '住院医生'),
)


# 医疗机构权限组分类标识(即权限组key)
GROUP_CATE_PROJECT_APPROVER = 'gp_project_approver'  # 项目分配者权限组key
GROUP_CATE_NORMAL_STAFF = 'gp_normal_staff'      # 普通员工权限组key

GROUP_CATE_CHOICES = (
    (GROUP_CATE_PROJECT_APPROVER, '项目分配人'),
    (GROUP_CATE_NORMAL_STAFF,     '普通员工'),
)
GROUP_CATE_DICT = dict(GROUP_CATE_CHOICES)


