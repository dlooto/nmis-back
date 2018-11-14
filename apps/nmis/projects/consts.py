# coding=utf-8
#
# Created by junn, on 2018/6/4
#

# 项目管理模块组常量配置

import logging

logger = logging.getLogger(__name__)


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

# 项目里程碑状态

PRO_MILESTONE_TODO = 'TODO'
PRO_MILESTONE_DOING = 'DOING'
PRO_MILESTONE_DONE = 'DONE'
PROJECT_MILESTONE_STATUS = (
    (PRO_MILESTONE_TODO, '未开始'),
    (PRO_MILESTONE_DOING, '进行中'),
    (PRO_MILESTONE_DONE, '已完结'),
)

# 项目类型
PRO_CATE_SOFTWARE = 'SW'
PRO_CATE_HARDWARE = 'HW'

PROJECT_CATE_CHOICES = (
    (PRO_CATE_SOFTWARE,    '信息化项目'),
    (PRO_CATE_HARDWARE,    '医疗器械项目'),
)

PRO_PUR_MTH_OPEN_BIDDING = 'OPEN'
PRO_PUR_MTH_INVITED_BIDDING = 'INVITED'
PRO_PUR_MTH_COMPETITIVE_NEGOTIATION = 'COMPETITIVE'
PRO_PUR_MTH_SINGLE_SOURCE_PROCUREMENT = 'SINGE'
PRO_PUR_MTH_METHOD_INQUIRY_PURCHASING = 'INQUIRY'


PROJECT_PURCHASE_METHOD_CHOICES = (
    (PRO_PUR_MTH_OPEN_BIDDING, '公开招标'),
    (PRO_PUR_MTH_INVITED_BIDDING, '邀请招标/选择性招标'),
    (PRO_PUR_MTH_COMPETITIVE_NEGOTIATION, '竞争性谈判/协商招标'),
    (PRO_PUR_MTH_SINGLE_SOURCE_PROCUREMENT, '单一来源采购'),
    (PRO_PUR_MTH_METHOD_INQUIRY_PURCHASING, '询价采购'),
)


PROJECT_DOCUMENT_DIR = 'upload/project/document/'
DOCUMENT_DIR = 'upload/document/'
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

DEFAULT_MILESTONE_REQUIREMENT_ARGUMENT = 'REQUIREMENT_ARGUMENT'
DEFAULT_MILESTONE_SELECT_PLAN = 'SELECT_PLAN'
DEFAULT_MILESTONE_PURCHASING_MANAGEMENT = 'PURCHASING_MANAGEMENT'
DEFAULT_MILESTONE_IMPLEMENTATION_ACCEPTANCE = 'IMPLEMENTATION_ACCEPTANCE'
DEFAULT_MILESTONE_RESEARCH = 'RESEARCH'
DEFAULT_MILESTONE_PLAN_GATHERED = 'PLAN_GATHERED'
DEFAULT_MILESTONE_PLAN_ARGUMENT = 'PLAN_ARGUMENT'
DEFAULT_MILESTONE_DETERMINE_PURCHASE_METHOD = 'DETERMINE_PURCHASE_METHOD'
DEFAULT_MILESTONE_STARTUP_PURCHASE = 'STARTUP_PURCHASE'
DEFAULT_MILESTONE_CONTRACT_MANAGEMENT = 'CONTRACT_MANAGEMENT'
DEFAULT_MILESTONE_CONFIRM_DELIVERY = 'CONFIRM_DELIVERY'
DEFAULT_MILESTONE_IMPLEMENTATION_DEBUGGING = 'IMPLEMENTATION_DEBUGGING'
DEFAULT_MILESTONE_PROJECT_CHECK = 'PROJECT_CHECK'

DEFAULT_MILESTONE_CHOICES = (
    (DEFAULT_MILESTONE_REQUIREMENT_ARGUMENT, '需求论证'),
    (DEFAULT_MILESTONE_SELECT_PLAN, '圈定方案'),
    (DEFAULT_MILESTONE_PURCHASING_MANAGEMENT, '采购管理'),
    (DEFAULT_MILESTONE_IMPLEMENTATION_ACCEPTANCE, '实施验收'),
    (DEFAULT_MILESTONE_RESEARCH, '调研'),
    (DEFAULT_MILESTONE_PLAN_GATHERED, '方案收集'),
    (DEFAULT_MILESTONE_PLAN_ARGUMENT, '方案论证'),
    (DEFAULT_MILESTONE_DETERMINE_PURCHASE_METHOD, '确定采购方式'),
    (DEFAULT_MILESTONE_STARTUP_PURCHASE, '启动采购'),
    (DEFAULT_MILESTONE_CONTRACT_MANAGEMENT, '合同管理'),
    (DEFAULT_MILESTONE_CONFIRM_DELIVERY, '到货'),
    (DEFAULT_MILESTONE_IMPLEMENTATION_DEBUGGING, '实施调试'),
    (DEFAULT_MILESTONE_PROJECT_CHECK, '项目验收'),
)
DEFAULT_MILESTONE_DICT = dict(DEFAULT_MILESTONE_CHOICES)
