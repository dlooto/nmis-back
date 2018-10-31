# coding=utf-8
#
# Created by junn, on 2018/5/29
#

#

import logging

from django.db import models

from base.models import BaseModel
from nmis.devices.consts import MGT_CATE_CHOICE, ASSERT_DEVICE_CATE_CHOICES, \
    ASSERT_DEVICE_CATE_MEDICAL, \
    ASSERT_DEVICE_STATUS_CHOICES, ASSERT_DEVICE_STATUS_FREE, ASSERT_DEVICE_STATE_CHOICES, \
    ASSERT_DEVICE_STATE_NEW, \
    PRIORITY_CHOICES, REPAIR_ORDER_STATUS_CHOICES, REPAIR_ORDER_STATUS_SUBMITTED, \
    REPAIR_ORDER_OPERATION_CHOICES, REPAIR_ORDER_OPERATION_SUBMIT, \
    MAINTENANCE_PLAN_TYPE_CHOICES, \
    MAINTENANCE_PLAN_TYPE_POLLING, MAINTENANCE_PLAN_STATUS_CHOICES, \
    MAINTENANCE_PLAN_STATUS_NEW, \
    MAINTENANCE_PLAN_PERIOD_MEASURE_CHOICES, MAINTENANCE_PLAN_PERIOD_MEASURE_DAY, \
    ASSERT_DEVICE_OPERATION_CHOICES, \
    ASSERT_DEVICE_OPERATION_SUBMIT, FAULT_SOLUTION_STATUS_CHOICES, \
    FAULT_SOLUTION_STATUS_NEW, ASSERT_DEVICE_STATUS_SCRAPPED, MAINTENANCE_PLAN_STATUS_DONE
from nmis.devices.managers import AssertDeviceManager, MedicalDeviceSix8CateManager, FaultTypeManager, \
    RepairOrderManager, MaintenancePlanManager, FaultSolutionManager

logger = logging.getLogger(__name__)


class Device(BaseModel):
    """
    一般设备/器械基础模型
    """
    name = models.CharField('设备名称', max_length=30)
    cate = models.CharField('设备类型', max_length=10, null=True, blank=True)
    producer = models.CharField('设备生产者', max_length=30, null=True, blank=True)

    class Meta:
        abstract = True


class OrderedDevice(Device):
    """
    申购的医疗设备, 一般作为申请项目里的硬件设备明细条目
    """
    project = models.ForeignKey(
        'projects.ProjectPlan', verbose_name='所属项目', related_name='ordered_devices', on_delete=models.CASCADE, null=True, blank=True
    )
    planned_price = models.FloatField('预算单价', default=0.00)
    real_price = models.FloatField('实际单价', default=0.00, null=True, blank=True)
    num = models.IntegerField('预购数量', default=1)
    measure = models.CharField('度量/单位', max_length=5, null=True, blank=True)
    type_spec = models.CharField('规格/型号', max_length=20, null=True, blank=True)
    purpose = models.CharField('用途', max_length=20, null=True, blank=True, default='')

    class Meta:
        verbose_name = u'申购的硬件设备'
        verbose_name_plural = u'申购的硬件设备'
        db_table = 'devices_ordered_device'
        permissions = (
            ('view_ordered_device', 'can view ordered device'),
        )

    VALID_ATTRS = [
        'name', 'cate', 'producer', "num", "planned_price", "measure",
        "type_spec", "purpose"
    ]

    def __str__(self):
        return self.name


class SoftwareDevice(Device):
    """
    申购的软件设备，一般作为申请项目里的软件设备条目明细
    """
    project = models.ForeignKey(
        'projects.ProjectPlan', verbose_name='所属项目', related_name='software_devices',
        on_delete=models.CASCADE, null=True, blank=True
    )
    purpose = models.CharField('用途', max_length=20, null=True, blank=True, default='')

    real_price = models.FloatField('实际单价', default=0.00, null=True, blank=True)
    planned_price = models.FloatField('预算单价', default=0.00)

    class Meta:
        verbose_name = '申购的软件设备'
        verbose_name_plural = verbose_name
        db_table = 'devices_software_device'
        permissions = (
            ('view_software_device', 'can view software device'),
        )

    VALID_ATTRS = [
        'name', 'cate', 'purpose'
    ]

    def __str__(self):
        return self.name

# class MedicalDevice(Device):
#     """
#     作为资产的医疗设备
#     """
#     medical_cate = models.CharField('医疗分类', max_length=3, default='')
#     license = models.ForeignKey()
#
#     class Meta:
#         verbose_name = u'医疗设备'
#         verbose_name_plural = u'医疗设备'
#         db_table = 'devices_medical_device'


class ContractDevice(Device):
    """
    软硬件产品信息, 作为合同明细条目
    """
    contract = models.ForeignKey(
        'projects.PurchaseContract', verbose_name='所属采购合同', on_delete=models.CASCADE,
        related_name='contract_devices',
        null=True, blank=True
    )
    supplier = models.CharField('供应商', max_length=100, null=True, blank=True)
    planned_price = models.FloatField('预算单价', default=0.00)
    real_price = models.FloatField('实际单价', default=0.00, null=True, blank=True)
    num = models.IntegerField('预购数量', default=1)
    real_total_amount = models.FloatField('总价', default=0.00, null=True, blank=True)
    measure = models.CharField('度量/单位', max_length=5, null=True, blank=True)
    type_spec = models.CharField('规格/型号', max_length=20, null=True, blank=True)
    purpose = models.CharField('用途', max_length=20, null=True, blank=True, default='')

    class Meta:
        verbose_name = '采购合同产品明细'
        verbose_name_plural = verbose_name
        db_table = 'devices_contract_device'
        permissions = (
            ('view_contract_device', 'can view contract device'),
        )

    VALID_ATTRS = [
        'name', 'cate', 'supplier',
        "real_price", "num", "real_total_amount",
        'producer',

    ]

    def __str__(self):
        return '%s %s' % (self.id, self.name)

    def deleted(self):
        """
        删除单个设备信息
        """
        try:
            self.clear_cache()
            self.delete()
        except Exception as e:
            logger.exception(e)
            return False
        return True


# ------------------------------------------------------------------ #
# ------------------------------ 设备管理 --------------------------- #
# ------------------------------------------------------------------ #


class MedicalDeviceSix8Cate(BaseModel):
    """
    医疗器械分类（68码）
    """
    code = models.CharField('分类编号', max_length=16, unique=True)
    title = models.CharField('分类名称', max_length=128, )
    level = models.SmallIntegerField('分类等级', default=1)
    parent = models.ForeignKey(
        'self', related_name='child_six8_cate', verbose_name='父级分类', on_delete=models.PROTECT,
        null=True, blank=True
    )
    example = models.TextField('品名举例', max_length=2048, null=True, blank=True)
    mgt_cate = models.SmallIntegerField('管理类别', choices=MGT_CATE_CHOICE, default=1)
    creator = models.ForeignKey(
        'hospitals.Staff', related_name='created_medical_device_cate', verbose_name='创建人', on_delete=models.PROTECT
    )

    objects = MedicalDeviceSix8CateManager()

    class Meta:
        verbose_name = ' 医疗器械分类(68码)'
        verbose_name_plural = verbose_name
        db_table = 'devices_medical_device_six8_cate'
        permissions = (
            ('view_medical_device_six8_cate', 'can view medical device six8 cate'),
        )

    VALID_ATTRS = [
        'code', 'title', 'parent', 'level', 'example', 'mgt_cate',
    ]

    def __str__(self):
        return '%d' % (self.id, )

    @property
    def signal(self):
        """
        编码代号：所属一级分类的code、title属性值拼接组成
        :return:
        """
        return '%s%s' % (self.parent.code, self.parent.code) if self.parent else ''


class AssertDevice(BaseModel):
    """
    资产设备
    """

    assert_no = models.CharField('资产编号', max_length=64, unique=True)
    title = models.CharField('资产名称', max_length=128, )
    cate = models.CharField('资产设备类型', choices=ASSERT_DEVICE_CATE_CHOICES, max_length=2, default=ASSERT_DEVICE_CATE_MEDICAL, )
    medical_device_cate = models.ForeignKey(
        'devices.MedicalDeviceSix8Cate', related_name='related_assert_device', verbose_name='医疗器械分类',
        on_delete=models.PROTECT, null=True
    )
    serial_no = models.CharField('资产序列号', max_length=64, unique=True)
    type_spec = models.CharField('规格型号', max_length=32, )
    service_life = models.SmallIntegerField('预计使用年限', )
    performer = models.ForeignKey(
        'hospitals.Staff', related_name='performed_assert_device', verbose_name='资产负责人',
        on_delete=models.PROTECT, null=True, blank=True
    )
    use_dept = models.ForeignKey(
        'hospitals.Department', related_name='used_assert_device', verbose_name='使用科室',
        on_delete=models.PROTECT, null=True, blank=True
    )
    responsible_dept = models.ForeignKey(
        'hospitals.Department', related_name='responsible_assert_device', verbose_name='负责科室',
        on_delete=models.PROTECT, null=True, blank=True
    )
    production_date = models.DateField('出厂日期',)
    bar_code = models.CharField('设备条形码', max_length=128, null=True, blank=True)
    producer = models.CharField('厂家', max_length=128, null=True, blank=True)
    storage_place = models.ForeignKey('hospitals.HospitalAddress', '存放地点', null=True, blank=True)
    purchase_date = models.DateField('购入日期')
    status = models.CharField('资产状态', max_length=3, choices=ASSERT_DEVICE_STATUS_CHOICES, default=ASSERT_DEVICE_STATUS_FREE)
    state = models.CharField('数据状态', max_length=3, choices=ASSERT_DEVICE_STATE_CHOICES, default=ASSERT_DEVICE_STATE_NEW)
    creator = models.ForeignKey(
        'hospitals.Staff', related_name='created_assert_device', verbose_name='创建人',
        on_delete=models.PROTECT
    )
    modifier = models.ForeignKey(
        'hospitals.Staff', related_name='modified_assert_device', verbose_name='修改人',
        on_delete=models.PROTECT, null=True, blank=True
    )
    modified_time = models.DateTimeField('修改时间', null=True, blank=True)

    objects = AssertDeviceManager()

    class Meta:
        verbose_name = '资产设备'
        verbose_name_plural = verbose_name
        db_table = 'devices_assert_device'
        permissions = (
            ('view_assert_device', 'can view assert device'),    # 查看设备
            ('scrap_assert_device', 'can scrap assert device'),  # 报废设备
            ('allocate_assert_device', 'can allocate assert device'),  # 调配设备
            ('import_fault_solution', 'can import fault_solution'),  # 导入设备
        )

    VALID_ATTRS = [
        'assert_no', 'title', 'cate', 'medical_device_cate', 'serial_no', 'type_spec',
        'service_life', 'performer', 'use_dept', 'responsible_dept', 'production_date',
        'bar_code', 'producer', 'storage_place', 'purchase_date', 'status', 'state', 'modifier', 'modified_time',
    ]

    def __str__(self):
        return '%d' % (self.id, )

    def deleted(self):

        try:
            self.clear_cache()
            self.delete()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def assert_device_scrapped(self):
        """
        资产设备报废
        """
        try:
            self.status = ASSERT_DEVICE_STATUS_SCRAPPED
            self.save()
            self.cache()
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def is_free(self):
        """
        设备处于闲置状态
        :return:
        """
        pass

    def is_using(self):
        """
        设备使用中
        :return:
        """
        pass

    def is_in_maintenance(self):
        """
        设备维修中
        :return:
        """
        pass

    def is_scrapped(self):
        """
        设备已报废
        :return:
        """
        pass

    def is_normal(self):
        """
        数据可正常使用
        :return:
        """
        pass


class AssertDeviceRecord(BaseModel):
    """
    设备变更记录
    """
    assert_device = models.ForeignKey(
        'devices.AssertDevice', verbose_name='资产设备', on_delete=models.PROTECT
    )
    operation = models.CharField('操作', choices=ASSERT_DEVICE_OPERATION_CHOICES, max_length=3, default=ASSERT_DEVICE_OPERATION_SUBMIT)
    reason = models.CharField('执行当前操作的原因', max_length=128, null=True, blank=True, default='')
    operator = models.ForeignKey(
        'hospitals.Staff', related_name='operate_assert_device_record', verbose_name='操作人', on_delete=models.PROTECT
    )
    # 调配给了谁
    receiver = models.ForeignKey(
        'hospitals.Staff', verbose_name='操作的接受方', on_delete=models.PROTECT, null=True, blank=True
    )
    msg_content = models.CharField('操作内容', max_length=128)

    class Meta:
        verbose_name = '设备变更记录'
        verbose_name_plural = verbose_name
        db_table = 'devices_assert_device_record'
        permissions = (
            ('view_assert_device_record', 'can view assert device record'),  # 查看设备变更记录
        )

    VALID_ATTRS = [
        'operation', 'msg_content', 'reason'
    ]

    def __str__(self):
        return '%d' % (self.id, )


class FaultType(BaseModel):
    """
    故障类型
    """
    title = models.CharField('故障类型名称', max_length=32, )
    desc = models.CharField('故障类型描述', max_length=255, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name='父类故障类型', on_delete=models.PROTECT, null=True, blank=True)
    # 祖节点到当节点的父节点最短路径, 由各节点id的字符串组成，每个id,之间用‘-’进行分隔
    parent_path = models.CharField('父类型路径', max_length=1024, default='', null=False, blank=False)
    level = models.SmallIntegerField('所属层级', default=1)
    sort = models.SmallIntegerField('排序码', default=1)
    creator = models.ForeignKey(
        'hospitals.Staff', related_name='created_fault_type', verbose_name='创建人',
        on_delete=models.PROTECT
    )

    objects = FaultTypeManager()

    class Meta:
        verbose_name = '故障类型'
        verbose_name_plural = verbose_name
        db_table = 'devices_fault_type'
        permissions = (
            ('view_fault_type', 'can view fault type'),  # 查看故障类型
        )

    VALID_ATTRS = [
        'title', 'desc', 'parent', 'level', 'sort',
    ]

    def __str__(self):
        return '%d' % (self.id, )


class RepairOrder(BaseModel):
    """
    报修单/维修工单
    """
    order_no = models.CharField('报修单号', max_length=64, unique=True)
    applicant = models.ForeignKey(
        'hospitals.Staff', related_name='applied_repair_order', verbose_name='报修人/申请人',
        on_delete=models.PROTECT
    )
    fault_type = models.ForeignKey('devices.FaultType', verbose_name='故障分类', on_delete=models.PROTECT)
    desc = models.CharField('故障描述', max_length=1024, null=True, blank=True)
    maintainer = models.ForeignKey(
        'hospitals.Staff', verbose_name='维修工程师', on_delete=models.PROTECT,
        null=True, blank=True
    )
    expenses = models.FloatField('维修费用', null=True, blank=True)
    result = models.CharField('处理结果', max_length=128, null=True, blank=True)
    solution = models.TextField('解决方案', max_length=2048, null=True, blank=True)
    # 存放id，id之间用分隔符分隔
    files = models.CharField('附件列表', max_length=16, null=True, blank=True)
    priority = models.CharField(
        '优先级', max_length=2, choices=PRIORITY_CHOICES, default='',
        null=True, blank=True
    )
    repair_devices = models.ManyToManyField(
        'devices.AssertDevice', verbose_name='报修设备清单',
        related_name="repair_device_list", blank=True
    )
    status = models.CharField('状态', max_length=3, choices=REPAIR_ORDER_STATUS_CHOICES, default=REPAIR_ORDER_STATUS_SUBMITTED)
    comment_grade = models.SmallIntegerField('评价等级', null=True, blank=True)
    comment_content = models.CharField('评价内容', max_length=128, null=True, blank=True)
    comment_time = models.DateTimeField('评价时间', null=True, blank=True)
    creator = models.ForeignKey('hospitals.Staff', related_name='created_repair_order', verbose_name='创建人', on_delete=models.PROTECT)
    modifier = models.ForeignKey(
        'hospitals.Staff', related_name='modified_repair_order', verbose_name='修改人',
        on_delete=models.PROTECT, null=True, blank=True
    )
    modified_time = models.DateTimeField('修改时间', null=True, blank=True)

    objects = RepairOrderManager()

    class Meta:
        verbose_name = '报修单/维修工单'
        verbose_name_plural = verbose_name
        db_table = 'devices_repair_order'
        permissions = (
            ('view_repair_order', 'can view repair order'),  # 查看报修单
            ('dispatch_repair_order', 'can dispatch repair order'),  # 分派报修单
        )

    VALID_ATTRS = [
        'applicant', 'fault_type', 'desc', 'maintainer', 'expenses', 'result', 'repair_device_list',
        'solution', 'files', 'priority', 'status', 'comment_grade', 'comment_content', 'comment_time',
        'modifier', 'modified_time'
    ]

    def __str__(self):
        return '%d' % (self.id, )

    def is_submitted(self):
        """
        报修单已提交/待分派
        :return:
        """
        pass

    def is_in_handle(self):
        """
         报修单处理中/已分派
        :return:
        """
        pass

    def is_done(self):
        """
        报修单已完成
        :return:
        """
        pass

    def is_commented(self):
        """
        报修单已被评价
        :return:
        """
        pass

    def get_repair_order_records(self):
        return RepairOrderRecord.objects.filter(repair_order=self)


class RepairOrderRecord(BaseModel):
    """
    报修单操作记录
    """
    repair_order = models.ForeignKey(
        'devices.RepairOrder', verbose_name='报修单/维修单', on_delete=models.PROTECT
    )
    operation = models.CharField(
        '操作', choices=REPAIR_ORDER_OPERATION_CHOICES, max_length=3, default=REPAIR_ORDER_OPERATION_SUBMIT
    )
    # 退回或关闭原因
    reason = models.CharField('执行当前操作的原因', max_length=128, null=True, blank=True, default='')
    operator = models.ForeignKey(
        'hospitals.Staff', related_name='operate_repair_order_record', verbose_name='操作人', on_delete=models.PROTECT
    )
    # 分派给谁
    receiver = models.ForeignKey(
        'hospitals.Staff', verbose_name='操作的接受方', on_delete=models.PROTECT, null=True, blank=True
    )
    msg_content = models.CharField('操作内容', max_length=128)

    class Meta:
        verbose_name = '报修单操作记录'
        verbose_name_plural = verbose_name
        db_table = 'devices_repair_order_record'
        permissions = (
            ('view_repair_order_record', 'can view repair order record'),  # 查看报修单操作记录
        )

    VALID_ATTRS = [
        'operation', 'msg_content', 'reason'
    ]

    def __str__(self):
        return '%d' % (self.id, )


class MaintenancePlan(BaseModel):
    """
    设备维护保养计划
    """

    plan_no = models.CharField('计划编号', max_length=64, unique=True)
    title = models.CharField('计划名称', max_length=32)
    places = models.ManyToManyField(
        'hospitals.HospitalAddress', verbose_name='维保地点列表',
        related_name="plan_place_ships", blank=True
    )
    type = models.CharField(
        '维保计划类型', choices=MAINTENANCE_PLAN_TYPE_CHOICES, default=MAINTENANCE_PLAN_TYPE_POLLING, max_length=3
    )
    start_date = models.DateTimeField('开始日期')
    period_measure = models.CharField(
        '执行周期计量单位', choices=MAINTENANCE_PLAN_PERIOD_MEASURE_CHOICES, default=MAINTENANCE_PLAN_PERIOD_MEASURE_DAY,
        max_length=2, null=True, blank=True
    )
    period_num = models.IntegerField('执行周期数', null=True, blank=True)
    expired_date = models.DateTimeField('截止日期')
    executor = models.ForeignKey(
        'hospitals.Staff', related_name='executed_maintenance_plan', verbose_name='执行人', on_delete=models.PROTECT
    )
    executed_date = models.DateTimeField('执行日期', null=True, blank=True)
    result = models.CharField('计划执行结果', max_length=128, null=True, blank=True)
    assert_devices = models.ManyToManyField(
        'devices.AssertDevice', verbose_name='计划维保设备清单',
        related_name="plan_device_list", blank=True
    )
    status = models.CharField(
        '状态', choices=MAINTENANCE_PLAN_STATUS_CHOICES, default=MAINTENANCE_PLAN_STATUS_NEW, max_length=3
    )
    creator = models.ForeignKey(
        'hospitals.Staff',  related_name='created_maintenance_plan', verbose_name='创建人', on_delete=models.PROTECT
    )
    modifier = models.ForeignKey(
        'hospitals.Staff',  related_name='modified_maintenance_plan', verbose_name='修改人', on_delete=models.PROTECT,
        null=True, blank=True
    )
    modified_time = models.DateTimeField('修改时间', null=True, blank=True)

    objects = MaintenancePlanManager()

    class Meta:
        verbose_name = '设备维护保养计划'
        verbose_name_plural = verbose_name
        db_table = 'devices_maintenance_plan'
        permissions = (
            ('view_maintenance_plan', 'can view maintenance plan'),  # 查看设备维护保养记录
        )

    VALID_ATTRS = [
        'title', 'places', 'type', 'start_date', 'period_measure', 'period_num', 'expired_date',
        'executor', 'executed_date', 'result', 'assert_devices', 'status', 'modifier', 'modified_time',
    ]

    def __str__(self):
        return '%d' % (self.id, )

    def change_status(self, result):
        """
        执行操作改变资产设备维护计划的状态：改为已执行状态
        :param result: 处理结果
        """
        try:
            self.result = result
            self.status = MAINTENANCE_PLAN_STATUS_DONE
            self.save()
            self.cache()
            return True
        except Exception as e:
            logger.exception(e)
            return False


class FaultSolution(BaseModel):
    """
    故障/问题解决方案
    """

    title = models.CharField('标题', max_length=128)
    desc = models.CharField('故障/问题描述', max_length=1024)
    fault_type = models.ForeignKey(
        'devices.FaultType', verbose_name='故障/问题分类',
        related_name='related_problem_solution', on_delete=models.PROTECT
    )
    solution = models.TextField('解决方案', max_length=2048)
    # 存放id，id之间用分隔符分隔
    files = models.CharField('附件列表', max_length=16, null=True, blank=True)
    status = models.CharField('状态', max_length=3, choices=FAULT_SOLUTION_STATUS_CHOICES, default=FAULT_SOLUTION_STATUS_NEW)
    page_views = models.IntegerField('浏览次数', null=True, blank=True)
    likes = models.IntegerField('点赞数', null=True, blank=True)
    creator = models.ForeignKey(
        'hospitals.Staff', verbose_name='创建人', related_name='created_problem_solution',
        on_delete=models.PROTECT
    )
    modifier = models.ForeignKey(
        'hospitals.Staff', verbose_name='修改人', related_name='modified_problem_solution',
        on_delete=models.PROTECT, null=True, blank=True)
    modified_time = models.DateTimeField('修改时间', null=True, blank=True)
    auditor = models.ForeignKey(
        'hospitals.Staff', verbose_name='审核人', related_name='audited_problem_solution',
        on_delete=models.PROTECT, null=True, blank=True
    )
    audited_time = models.DateTimeField('审核时间', null=True, blank=True)

    objects = FaultSolutionManager()

    class Meta:
        verbose_name = '故障/问题解决方案'
        verbose_name_plural = verbose_name
        db_table = 'devices_fault_solution'
        permissions = (
            ('view_fault_solution', 'can view fault solution'),   # 查看故障/问题解决方案
            ('import_fault_solution', 'can import fault solution'),   # 导入故障/问题解决方案
            ('export_fault_solution', 'can export fault solution'),   # 导出故障/问题解决方案
            ('audit_fault_solution', 'can audit fault solution'),   # 审核故障/问题解决方案
        )

    VALID_ATTRS = [
        'title', 'desc', 'fault_type', 'solution', 'files',
        'status', 'page_views', 'likes', 'modifier', 'modified_time', 'auditor', 'audited_time',
    ]

    def __str__(self):
        return '%d' % (self.id, )
