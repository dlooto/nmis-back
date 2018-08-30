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
DPT_ATTRI_OTHER = 'OT'

DPT_ATTRI_CHOICES = (
    (DPT_ATTRI_MEDICAL, '医技'),
    (DPT_ATTRI_SUPPORT, '后勤'),
    (DPT_ATTRI_OFFICE,  '行政'),
    (DPT_ATTRI_OTHER,   '其他'),
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


# 权限组: 医疗机构权限组分类标识(即权限组key)
GROUP_CATE_PROJECT_APPROVER = 'GPA'  # 项目分配者权限组key
GROUP_CATE_NORMAL_STAFF = 'GNS'      # 普通员工权限组key
GROUP_CATE_ROLE = 'GCR'     # 角色类key
GROUP_CATE_USER = 'GCU'     # 用户类key

GROUP_CATE_CHOICES = (
    (GROUP_CATE_PROJECT_APPROVER, '项目分配人'),
    (GROUP_CATE_NORMAL_STAFF,     '普通员工'),
    (GROUP_CATE_ROLE, '角色类'),
    (GROUP_CATE_USER, '用户类')
)
GROUP_CATE_DICT = dict(GROUP_CATE_CHOICES)

GROUPS = {
    'admin': {
        'name': u'管理员',
        'cate': '',
        'desc': '* 管理系统所有功能及信息'
    },
    GROUP_CATE_PROJECT_APPROVER:   {
        'name': u'项目分配人',
        'cate': GROUP_CATE_PROJECT_APPROVER,
        'desc': u'为申请的项目指定责任人'
    },
    GROUP_CATE_NORMAL_STAFF: {
        'name': u'普通员工',
        'cate': GROUP_CATE_NORMAL_STAFF,
        'desc': u'机构普通员工'
    },
    GROUP_CATE_ROLE: {
        'name': u'角色类',
        'cate': GROUP_CATE_ROLE,
        'desc': u'角色类分组'
    },
    GROUP_CATE_USER: {
        'name': u'用户类',
        'cate': GROUP_CATE_USER,
        'desc': u'用户类分组'
    },
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
    'dept_attri':   '科室属性',
    'desc':         '职能描述'
}


# 文档类型
ARCHIVE = {
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xltx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
    '.xlsm': 'application/vnd.ms-excel.sheet.macroEnabled.12',
    '.xltm': 'application/vnd.ms-excel.template.macroEnabled.12',
    '.xlam': 'application/vnd.ms-excel.addin.macroEnabled.12',
    '.xlsb': 'application/vnd.ms-excel.sheet.binary.macroEnabled.12',

    '.xla': 'application/vnd.ms-excel',
    '.xlc': 'application/vnd.ms-excel',
    '.xlm': 'application/vnd.ms-excel',
    '.xls': 'application/vnd.ms-excel',
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



