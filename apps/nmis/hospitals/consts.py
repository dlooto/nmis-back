# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 医疗机构模块常量配置

import logging

logger = logging.getLogger(__name__)


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
DPT_ATTRI_OTHER = 'OT'

DPT_ATTRI_CHOICES = (
    (DPT_ATTRI_MEDICAL, '医技'),
    (DPT_ATTRI_SUPPORT, '后勤'),
    (DPT_ATTRI_OFFICE,  '行政'),
    (DPT_ATTRI_OTHER,   '其他'),
)

HOSPITAL_AREA_TYPE_BUILDING = 'BD'
HOSPITAL_AREA_TYPE_FLOOR = 'FR'
HOSPITAL_AREA_TYPE_ROOM = 'RM'


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

ROLE_CATE_NORMAL = 'CNM'

ROLE_CATE_CHOICES = (
    (ROLE_CATE_NORMAL, '普通角色类'),
)

ROLE_CODE_HOSP_SUPER_ADMIN = 'HOS-SUP-ADM'
ROLE_CODE_SYSTEM_SETTING_ADMIN = 'SYS-SET-ADM'

ROLE_CODE_NORMAL_STAFF = 'HOS-NOR-STF'
ROLE_CODE_HOSP_REPORT_ASSESS = 'HOS-RPT-ASS'

ROLE_CODE_ASSERT_DEVICE_ADMIN = 'DEV-ASS-ADM'
ROLE_CODE_REPAIR_ORDER_DISPATCHER = 'DEV-REO-DIS'
ROLE_CODE_MAINTAINER = 'DEV-MAI'
ROLE_CODE_PRO_DISPATCHER = 'PRO-DIS'

ROLE_CODE_CHOICES = (
    (ROLE_CODE_NORMAL_STAFF, '普通员工'),
    (ROLE_CODE_HOSP_SUPER_ADMIN, '超级管理员'),
    (ROLE_CODE_SYSTEM_SETTING_ADMIN, '系统管理员'),
    (ROLE_CODE_ASSERT_DEVICE_ADMIN, '资产管理员'),
    (ROLE_CODE_REPAIR_ORDER_DISPATCHER, '维修任务分配者'),
    (ROLE_CODE_MAINTAINER, '维修工程师'),
    (ROLE_CODE_HOSP_REPORT_ASSESS, '统计信息查看者'),
    (ROLE_CODE_PRO_DISPATCHER, '项目分配者')
)

ROLES = {
    ROLE_CODE_NORMAL_STAFF: {
        'name': '普通员工',
        'codename': ROLE_CODE_NORMAL_STAFF,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_HOSP_SUPER_ADMIN: {
        'name': '超级管理员',
        'codename': ROLE_CODE_HOSP_SUPER_ADMIN,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_SYSTEM_SETTING_ADMIN: {
        'name': '系统管理员',
        'codename': ROLE_CODE_SYSTEM_SETTING_ADMIN,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_ASSERT_DEVICE_ADMIN: {
        'name': '资产管理员',
        'codename': ROLE_CODE_ASSERT_DEVICE_ADMIN,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_REPAIR_ORDER_DISPATCHER: {
        'name': '维修任务分配者',
        'codename': ROLE_CODE_REPAIR_ORDER_DISPATCHER,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_MAINTAINER: {
        'name': '维修工程师',
        'codename': ROLE_CODE_MAINTAINER,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_HOSP_REPORT_ASSESS: {
        'name': '统计信息查看者',
        'codename': ROLE_CODE_HOSP_REPORT_ASSESS,
        'cate': ROLE_CATE_NORMAL
    },
    ROLE_CODE_PRO_DISPATCHER: {
        'name': '项目分配者',
        'codename': ROLE_CODE_PRO_DISPATCHER,
        'cate': ROLE_CATE_NORMAL
    }
}

SEQ_REPAIR_ORDER_NO = 'SEQ_REP_ORD_NO'
SEQ_MAINTAIN_PLAN_NO = 'SEQ_MAI_PLA_NO'

SEQ_CODE_CHOICES = (
    (SEQ_REPAIR_ORDER_NO, '报修单自增序列'),
    (SEQ_MAINTAIN_PLAN_NO, '维护保养计划自增序列'),
)

SEQUENCES = {
    SEQ_REPAIR_ORDER_NO: {
        "seq_code": SEQ_REPAIR_ORDER_NO,
        "seq_name": "报修单自增序列",
        "seq_value": 0,
        "increment": 1,
        "remark": "用于报修单序列"
    },
    SEQ_MAINTAIN_PLAN_NO: {
        "seq_code": SEQ_MAINTAIN_PLAN_NO,
        "seq_name": "维护保养计划自增序列",
        "seq_value": 0,
        "increment": 1,
        "remark": "用于维护保养计划序列"
    }
}

# 上传的员工excel模板文件表头字典
UPLOADED_STAFF_EXCEL_HEADER_DICT = {
    'username':      '用户名',
    'staff_name':    '员工姓名',
    'email':         '邮箱',
    'contact_phone': '联系电话',
    'dept_name':     '所属科室'
}

# 上传的部门excel模板文件表头字典
UPLOADED_DEPT_EXCEL_HEADER_DICT = {
    'dept_name':    '科室名称',
    # 'dept_attri':   '科室属性',
    'desc':         '职能描述',
}


# 文档类型
ARCHIVE = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xlsx-wps': 'application/wps-office.xlsx',
    '.xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    '.xltm': 'application/vnd.ms-excel.template.macroEnabled.12',
    '.xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
    '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',

    '.xla': 'application/vnd.ms-excel',
    '.xlc': 'application/vnd.ms-excel',
    '.xlm': 'application/vnd.ms-excel',
    '.xls': 'application/vnd.ms-excel',
    '.xls-wps': 'application/wps-office.xls',
    '.xlt': 'application/vnd.ms-excel',
    '.xlw': 'application/vnd.ms-excel',

    '.doc': 'application/msword',
    '.dot': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.dotx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    '.docm': 'application/vnd.ms-word.template.macroEnabled.12',
    '.wps': 'application/vnd.ms-works',

    '.pot': 'application/vnd.ms-powerpoint',
    '.pps': 'application/vnd.ms-powerpoint',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',

    '.rar': 'application/octet-stream',
    '.zip': 'application/zip',

    '.pdf': 'application/pdf',
    '.txt': 'text/plain',
    '.jpe': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',
    '.jpz': 'image/jpeg',
    '.png': 'image/png',
    '.pnz': 'image/png',
    '.gif': 'image/gif',
    '.ico': 'image/x-icon',
    '.bmp': 'image/bmp',

}



