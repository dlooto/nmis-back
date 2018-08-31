# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 项目管理模块组常量配置

import logging

logs = logging.getLogger(__name__)


# 项目申请状态
PRO_STATUS_PENDING = 'PE'
PRO_STATUS_STARTED = 'SD'
PRO_STATUS_DONE = 'DO'
PRO_STATUS_OVERRULE = 'OR'
PRO_STATUS_PAUSE = 'PA'

PROJECT_STATUS_CHOICES = (
    (PRO_STATUS_PENDING,    '未开始'),
    (PRO_STATUS_STARTED,    '已启动'),
    (PRO_STATUS_DONE,       '已完成'),
    (PRO_STATUS_OVERRULE,    '已驳回'),
    (PRO_STATUS_PAUSE,       '已挂起'),
)
# 项目操作日志类型
PRO_OPERATION_OVERRULE = 'overrule'
PRO_OPERATION_PAUSE = 'pause'

PROJECT_OPERATION_CHOICES = (
    (PRO_OPERATION_OVERRULE,    '驳回'),
    (PRO_OPERATION_PAUSE,    '挂起'),
)

# 项目申请办理方式
PRO_HANDING_TYPE_SELF = 'SE'
PRO_HANDING_TYPE_AGENT = 'AG'

PROJECT_HANDING_TYPE_CHOICES = (
    (PRO_HANDING_TYPE_SELF,     '自行办理'),
    (PRO_HANDING_TYPE_AGENT,    '转交办理'),
)

# 项目流程结束标识
FLOW_DONE = 'DN'
FLOW_UNDONE = 'UN'
FLOW_DONE_SIGN = (
    (FLOW_DONE, '项目流程结束'),
    (FLOW_UNDONE, '项目流程未结束'),
)

# 项目类型
PRO_CATE_SOFTWARE = 'SW'
PRO_CATE_HARDWARE = 'HW'

PROJECT_CATE_CHOICES = (
    (PRO_CATE_SOFTWARE,    '信息化项目'),
    (PRO_CATE_HARDWARE,    '医疗器械项目'),
)


PROJECT_DOCUMENT_DIR = 'upload/project/document/'

# 项目文档类型
PRO_DOC_CATE_PRODUCT = 'product'
PRO_DOC_CATE_PRODUCER = 'producer'
PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN = 'supplier_selection_plan'
PRO_DOC_CATE_PLAN_ARGUMENT = 'plan_argument'
PRO_DOC_CATE_DECISION_ARGUMENT = 'decision_argument'
PRO_DOC_CATE_BIDDING_DOC = 'bidding_doc'
PRO_DOC_CATE_TENDER_DOC = 'tender_doc'
PRO_DOC_CATE_PURCHASE_PLAN = 'purchase_plan'
PRO_DOC_CATE_CONTRACT = 'contract'
PRO_DOC_CATE_DELIVERY_NOTE = 'delivery_note'
PRO_DOC_CATE_IMPLEMENT_PLAN = 'implement_plan'
PRO_DOC_CATE_IMPLEMENT_RECORD = 'implement_record'
PRO_DOC_CATE_IMPLEMENT_SUMMARY = 'implement_summary'
PRO_DOC_CATE_ACCEPTANCE_PLAN = 'acceptance_plan'
PRO_DOC_CATE_ACCEPTANCE_REPORT = 'acceptance_report'
PRO_DOC_CATE_OTHERS = 'others'

PROJECT_DOCUMENT_CATE_CHOICES = (
    (PRO_DOC_CATE_PRODUCT, '产品资料'),
    (PRO_DOC_CATE_PRODUCER, '厂商资料'),
    (PRO_DOC_CATE_SUPPLIER_SELECTION_PLAN, '供应商选择方案'),
    (PRO_DOC_CATE_PLAN_ARGUMENT, '方案论证资料'),
    (PRO_DOC_CATE_DECISION_ARGUMENT, '决策论证'),
    (PRO_DOC_CATE_BIDDING_DOC, '招标文件'),
    (PRO_DOC_CATE_TENDER_DOC, '投标文件'),
    (PRO_DOC_CATE_PURCHASE_PLAN, '采购计划'),
    (PRO_DOC_CATE_CONTRACT, '合同'),
    (PRO_DOC_CATE_DELIVERY_NOTE, '送货单'),
    (PRO_DOC_CATE_IMPLEMENT_PLAN, '实施方案'),
    (PRO_DOC_CATE_IMPLEMENT_RECORD, '实施日志'),
    (PRO_DOC_CATE_IMPLEMENT_SUMMARY, '实施总结'),
    (PRO_DOC_CATE_ACCEPTANCE_PLAN, '验收方案'),
    (PRO_DOC_CATE_ACCEPTANCE_REPORT, '验收报告'),
    (PRO_DOC_CATE_OTHERS, '其他资料'),
)