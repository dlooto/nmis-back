# coding=utf-8
#
# Created by gong, on 2018/6/4
#

# 设备模块常量配置

import logging
from enum import Enum

from nmis.hospitals.consts import SEQ_REPAIR_ORDER_NO, SEQ_MAINTAIN_PLAN_NO
from utils.eggs import BaseEnum

logger = logging.getLogger(__name__)

# 医疗器械分类管理类型
MGT_CATE_CHOICE = (
    (1, 'Ⅰ类'),
    (2, 'Ⅱ类'),
    (3, 'Ⅲ类'),
)

# 资产设备类型
ASSERT_DEVICE_CATE_MEDICAL = 'ME'
ASSERT_DEVICE_CATE_INFORMATION = 'IN'
ASSERT_DEVICE_CATE_CHOICES = (
    (ASSERT_DEVICE_CATE_MEDICAL, '医疗设备'),
    (ASSERT_DEVICE_CATE_INFORMATION, '信息化设备'),
)
# 资产设备状态
ASSERT_DEVICE_STATUS_FREE = 'FR'
ASSERT_DEVICE_STATUS_IN_MAINTENANCE = 'IM'
ASSERT_DEVICE_STATUS_USING = 'US'
ASSERT_DEVICE_STATUS_SCRAPPED = 'SC'
ASSERT_DEVICE_STATUS_CHOICES = (
    (ASSERT_DEVICE_STATUS_FREE, '闲置'),
    (ASSERT_DEVICE_STATUS_USING, '使用中'),
    (ASSERT_DEVICE_STATUS_IN_MAINTENANCE, '维修中'),
    (ASSERT_DEVICE_STATUS_SCRAPPED, '已报废'),

)

# 资产设备数据状态
ASSERT_DEVICE_STATE_NEW = 'NW'
ASSERT_DEVICE_STATE_NORMAL = 'NL'
ASSERT_DEVICE_STATE_CHOICES = (
    (ASSERT_DEVICE_STATE_NEW, '新建'),
    (ASSERT_DEVICE_STATE_NORMAL, '正常'),
)

# 资产设备变更操作类型
ASSERT_DEVICE_OPERATION_SUBMIT = 'SMT'
ASSERT_DEVICE_OPERATION_ALLOCATION = 'LAC'
ASSERT_DEVICE_OPERATION_SCRAP = 'SCP'
ASSERT_DEVICE_OPERATION_REPAIR = 'RPR'
ASSERT_DEVICE_OPERATION_CHOICES = (
    (ASSERT_DEVICE_OPERATION_SUBMIT, '提交'),
    (ASSERT_DEVICE_OPERATION_ALLOCATION, '调配'),
    (ASSERT_DEVICE_OPERATION_SCRAP, '报废'),
    (ASSERT_DEVICE_OPERATION_REPAIR, '维修'),
)

# 报修单优先级
PRIORITY_LOW = "L"
PRIORITY_MEDIUM = "M"
PRIORITY_HIGH = "H"
PRIORITY_EMERGENCY = "E"
PRIORITY_URGENT = "U"

PRIORITY_CHOICES = (
    (PRIORITY_LOW, '低'),
    (PRIORITY_MEDIUM, '中'),
    (PRIORITY_HIGH, '高'),
    (PRIORITY_EMERGENCY, '紧急'),
    (PRIORITY_URGENT, '非常紧急'),
)
# 报修单状态
REPAIR_ORDER_STATUS_SUBMITTED = 'SMT'
REPAIR_ORDER_STATUS_DOING = 'DNG'
REPAIR_ORDER_STATUS_DONE = 'DNE'
REPAIR_ORDER_STATUS_RETURNED = 'RTN'
REPAIR_ORDER_STATUS_CLOSED = 'CLS'
REPAIR_ORDER_STATUS_CHOICES = (
    (REPAIR_ORDER_STATUS_SUBMITTED, '已提交/待分派'),
    (REPAIR_ORDER_STATUS_DOING, '处理中/已分派'),
    (REPAIR_ORDER_STATUS_DONE, '已处理'),
    (REPAIR_ORDER_STATUS_RETURNED, '已退回'),
    (REPAIR_ORDER_STATUS_CLOSED, '已关闭'),
)
# 报修单操作类型
REPAIR_ORDER_OPERATION_SUBMIT = 'SMT'
REPAIR_ORDER_OPERATION_DISPATCH = 'DSP'
REPAIR_ORDER_OPERATION_HANDLE = 'HDL'
REPAIR_ORDER_OPERATION_COMMENT = 'CMT'
REPAIR_ORDER_OPERATION_RETURN = 'RTN'
REPAIR_ORDER_OPERATION_CLOSE = 'CLS'
REPAIR_ORDER_OPERATION_CHOICES = (
    (REPAIR_ORDER_OPERATION_SUBMIT, '提交'),
    (REPAIR_ORDER_OPERATION_DISPATCH, '分派'),
    (REPAIR_ORDER_OPERATION_RETURN, '退回'),
    (REPAIR_ORDER_OPERATION_HANDLE, '处理'),
    (REPAIR_ORDER_OPERATION_COMMENT, '评价'),
    (REPAIR_ORDER_OPERATION_CLOSE, '关闭')
)
# 保修列表请求操作类型
MY_REPAIR_ORDERS = 'MRO'
TO_DISPATCH_ORDERS = 'TDO'
MY_MAINTAIN_ORDERS = 'MMO'
ALL_ORDERS = 'ALO'
ORDERS_ACTION_CHOICES = {
    MY_REPAIR_ORDERS: '我的报修',  # 当前操作人的创建的
    TO_DISPATCH_ORDERS: '待分派',  # 所有人已提交的
    MY_MAINTAIN_ORDERS: '我的维修',  # 所有分派给当前操作人的
    ALL_ORDERS: '所有报修单'
}

# 设备维护计划类型
MAINTENANCE_PLAN_TYPE_POLLING = 'PL'
MAINTENANCE_PLAN_TYPE_UPKEEP = 'UK'
MAINTENANCE_PLAN_TYPE_STOCKTAKE = 'ST'

MAINTENANCE_PLAN_TYPE_CHOICES = (
    (MAINTENANCE_PLAN_TYPE_POLLING, '巡检'),
    (MAINTENANCE_PLAN_TYPE_UPKEEP, '保养'),
    (MAINTENANCE_PLAN_TYPE_STOCKTAKE, '盘点'),
)
# 设备维护计划状态
MAINTENANCE_PLAN_STATUS_NEW = "NW"
MAINTENANCE_PLAN_STATUS_DONE = 'DN'
MAINTENANCE_PLAN_STATUS_CHOICES = (
    (MAINTENANCE_PLAN_STATUS_NEW, ' 新建/未执行'),
    (MAINTENANCE_PLAN_STATUS_DONE, '已执行')
)
MAINTENANCE_PLAN_PERIOD_MEASURE_YEAR = 'Y'
MAINTENANCE_PLAN_PERIOD_MEASURE_MONTH = 'M'
MAINTENANCE_PLAN_PERIOD_MEASURE_WEEK = 'W'
MAINTENANCE_PLAN_PERIOD_MEASURE_DAY = 'D'

MAINTENANCE_PLAN_PERIOD_MEASURE_CHOICES = (
    ('MAINTENANCE_PLAN_PERIOD_MEASURE_YEAR', '年'),
    ('MAINTENANCE_PLAN_PERIOD_MEASURE_MONTH', '月'),
    ('MAINTENANCE_PLAN_PERIOD_MEASURE_WEEK', '周'),
    ('MAINTENANCE_PLAN_PERIOD_MEASURE_DAY', '日'),
)
MAINTENANCE_PLAN_EXPIRED_DATE_ON_MONTH = 'OM'
MAINTENANCE_PLAN_EXPIRED_DATE_ON_WEEK = 'OW'
MAINTENANCE_PLAN_EXPIRED_DATE_THREE_DAY = 'TD'
MAINTENANCE_PLAN_EXPIRED_DATE_NOW_DAY = 'ND'
MAINTENANCE_PLAN_EXPIRED_DATE_BE_OVERDUE = 'BO'

MAINTENANCE_PLAN_EXPIRED_DATE_CHOICES = (
    (MAINTENANCE_PLAN_EXPIRED_DATE_ON_MONTH, '一个月内到期'),
    (MAINTENANCE_PLAN_EXPIRED_DATE_ON_WEEK, '一周内到期'),
    (MAINTENANCE_PLAN_EXPIRED_DATE_THREE_DAY, '三天内到期'),
    (MAINTENANCE_PLAN_EXPIRED_DATE_NOW_DAY, '今天到期'),
    (MAINTENANCE_PLAN_EXPIRED_DATE_BE_OVERDUE, '逾期'),
)

# 故障/问题解决方案状态
FAULT_SOLUTION_STATUS_NEW = 'NW'
FAULT_SOLUTION_STATUS_NORMAL = 'NM'
FAULT_SOLUTION_STATUS_CHOICES = (
    (FAULT_SOLUTION_STATUS_NEW, '新建/待审核'),
    (FAULT_SOLUTION_STATUS_NORMAL, '正常'),
)
# 报修单自增序列编码
REPAIR_ORDER_NO_SEQ_CODE = SEQ_REPAIR_ORDER_NO
# 报修单自增序列标识支持的最大位数
REPAIR_ORDER_NO_SEQ_DIGITS = 3
# 报修单编号前缀
REPAIR_ORDER_NO_PREFIX = 'NB'
MAINTENANCE_PLAN_NO_PREFIX = 'HP'

# 维护保养计划自增序列编码
MAINTENANCE_PLAN_NO_SEQ_CODE = SEQ_MAINTAIN_PLAN_NO
# 维护单自增序列标识支持的最大位数
MAINTENANCE_PLAN_NO_SEQ_DIGITS = 3


# 上传的医疗资产设备excel模板文件表头字典
UPLOADED_MEDICAL_ASSERT_DEVICE_EXCEL_HEADER_DICT = {
    'assert_no':                    '资产编号',
    'title':                        '资产名称',
    'medical_device_cate':          '医疗设备分类',
    'code':                         '分类编号',
    'serial_no':                    '资产序列号',
    'type_spec':                    '规格型号',
    'service_life':                 '预计使用年限',
    'performer':                    '资产负责人',
    'responsible_dept':             '负责部门',
    'use_dept':                     '使用部门',
    'production_date':              '出厂日期',
    'bar_code':                     '设备条形码',
    'status':                       '资产状态',
    'storage_place':                '存储地点',
    'producer':                     '厂家',
    'purchase_date':                '购入日期',
}

# 上传的信息化资产设备excel模板文件表头字典
UPLOADED_INFORMATION_ASSERT_DEVICE_EXCEL_HEADER_DICT = {
    'assert_no':                    '资产编号',
    'title':                        '资产名称',
    'serial_no':                    '资产序列号',
    'type_spec':                    '规格型号',
    'service_life':                 '预计使用年限',
    'performer':                    '资产负责人',
    'responsible_dept':             '负责部门',
    'use_dept':                     '使用部门',
    'production_date':              '出厂日期',
    'bar_code':                     '设备条形码',
    'status':                       '资产状态',
    'storage_place':                '存储地点',
    'producer':                     '厂家',
    'purchase_date':                '购入日期',
}

# 导入故障/问题解决方案excel模板文件表头字典
UPLOADED_FS_EXCEL_HEAD_DICT = {
    'title':             '标题',
    'fault_type_title':        '故障类型',
    'solution':          '解决方案',
}


class OrderPriorityEnum(BaseEnum):
    LOW = ("L", "低")
    MEDIUM = ("M", "中")
    HIGH = ("H", "高")
    EMERGENCY = ("E", "紧急")
    URGENT = ("U", "非常紧急")


class MdcManageCateEnum(BaseEnum):
    """
    医疗器械管理类别枚举
    """
    FIRST = (1, "Ⅰ")
    SECOND = (2, "Ⅱ")
    THIRD = (3, "Ⅲ")


# 医疗器械分类上传文件表头字典
UPLOADED_MEDICAL_DEVICE_CATE_EXCEL_HEADER_DICT = {
    'catalog':                  '目录名称',
    'first_level_cate':         '一级产品类别',
    'second_level_cate':        '二级产品类别',
    'code':                     '分类编码',
    'desc':                     '产品描述',
    'purpose':                  '预期用途',
    'example':                  '品名举例',
    'mgt_cate':                 '管理类别',
}