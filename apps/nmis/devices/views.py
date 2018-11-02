# coding=utf-8
#
# Created by gong, on 2018-10-16
#

import logging

from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, F

import settings
from base import resp
from base.common.decorators import check_params_not_null, check_id
from base.common.param_utils import get_id_list
from base.views import BaseAPIView
from nmis.devices.consts import ASSERT_DEVICE_STATUS_CHOICES, REPAIR_ORDER_STATUS_CHOICES, \
    REPAIR_ORDER_OPERATION_CHOICES, REPAIR_ORDER_OPERATION_DISPATCH, \
    REPAIR_ORDER_OPERATION_HANDLE, REPAIR_ORDER_OPERATION_COMMENT, \
    ASSERT_DEVICE_CATE_CHOICES, \
    REPAIR_ORDER_STATUS_SUBMITTED, ORDERS_ACTION_CHOICES, MY_REPAIR_ORDERS, \
    MY_MAINTAIN_ORDERS, ALL_ORDERS, \
    TO_DISPATCH_ORDERS, REPAIR_ORDER_STATUS_DOING, REPAIR_ORDER_STATUS_DONE, \
    MAINTENANCE_PLAN_STATUS_CHOICES, MAINTENANCE_PLAN_EXPIRED_DATE_CHOICES, \
    MAINTENANCE_PLAN_STATUS_DONE, UPLOADED_FS_EXCEL_HEAD_DICT, ASSERT_DEVICE_CATE_MEDICAL, \
    UPLOADED_MEDICAL_ASSERT_DEVICE_EXCEL_HEADER_DICT, \
    UPLOADED_INFORMATION_ASSERT_DEVICE_EXCEL_HEADER_DICT
from nmis.devices.forms import AssertDeviceCreateForm, AssertDeviceUpdateForm, \
    RepairOrderCreateForm, MaintenancePlanCreateForm, RepairOrderHandleForm, RepairOrderCommentForm, \
    RepairOrderDispatchForm, FaultSolutionCreateForm, FaultSolutionsImportForm, AssertDeviceBatchUploadForm

from nmis.devices.models import AssertDevice, MedicalDeviceSix8Cate, RepairOrder, \
    FaultType, FaultSolution, MaintenancePlan
from nmis.devices.permissions import AssertDeviceAdminPermission, RepairOrderCreatorPermission, \
    MaintenancePlanExecutePermission, RepairOrderHandlePermission, RepairOrderDispatchPermission, \
    KnowledgeManagePermission
from nmis.documents.consts import FILE_CATE_CHOICES, DOC_DOWNLOAD_BASE_DIR, DOC_UPLOAD_BASE_DIR
from nmis.documents.forms import FileBulkCreateOrUpdateForm
from nmis.hospitals.consts import ARCHIVE, ROLE_CODE_HOSP_SUPER_ADMIN, \
    ROLE_CODE_NORMAL_STAFF, ROLE_CODE_ASSERT_DEVICE_ADMIN
from nmis.hospitals.models import Staff, Department, HospitalAddress
from nmis.devices.serializers import RepairOrderSerializer, FaultSolutionSerializer
from nmis.hospitals.permissions import IsHospSuperAdmin, SystemManagePermission, HospGlobalReportAssessPermission, \
    HospitalStaffPermission
from utils import times, files
from utils.files import ExcelBasedOXL, file_read_iterator

logger = logging.getLogger(__name__)


class AssertDeviceListView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    def get(self, req):
        """
        获取资产设备列表（
        筛选条件：关键词搜索（设备名称）、设备状态（维修、使用中、报废、闲置）、资产存储地点、设备类型
        ）
        """
        self.check_object_any_permissions(req, req.user)
        search_key = req.GET.get('search_key')
        str_status = req.GET.get('status')
        cate = req.GET.get('cate')
        storage_place_ids = get_id_list(req.GET.get('storage_place_ids', '').strip())
        if cate:
            if cate not in dict(ASSERT_DEVICE_CATE_CHOICES):
                return resp.failed('资产设备类型错误')
        storage_places = HospitalAddress.objects.get_hospital_address_by_ids(storage_place_ids)
        if len(storage_places) < len(storage_place_ids):
            return resp.failed('请确认是否有不存在的存储地点信息')

        status_list = None
        if str_status:
            status_list = list(set([status.strip() for status in str_status.split(',')]))
            logger.info(status_list)
            for status in status_list:
                if status not in dict(ASSERT_DEVICE_STATUS_CHOICES):
                    return resp.failed('资产设备状态错误')

        assert_devices = AssertDevice.objects.get_assert_devices(
            cate=cate, search_key=search_key, status=status_list, storage_places=storage_places)
        self.get_pages(assert_devices, results_name='assert_devices')
        return self.get_pages(assert_devices, results_name='assert_devices')


class AssertDeviceCreateView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    @check_params_not_null(['assert_no', 'title', 'serial_no',
                            'type_spec', 'service_life', 'production_date',
                            'status', 'storage_place_id', 'purchase_date', 'cate'])
    def post(self, req):
        """
        创建资产设备
        :param req:
        :return:
        """
        self.check_object_any_permissions(req, req.user)
        self.get_object_or_404(req.data.get('performer_id'), Staff)
        self.get_object_or_404(req.data.get('responsible_dept_id'), Department)
        self.get_object_or_404(req.data.get('use_dept_id'), Department)
        if req.data.get('medical_device_cate_id'):
            self.get_object_or_404(req.data.get('medical_device_cate_id'), MedicalDeviceSix8Cate)
        self.get_object_or_404(req.data.get('storage_place_id'), HospitalAddress)
        creator = req.user.get_profile()
        form = AssertDeviceCreateForm(creator, req.data)
        if not form.is_valid():
            return resp.failed(form.errors)
        assert_device = form.save()
        if not assert_device:
            return resp.failed('操作失败')
        return resp.serialize_response(assert_device, results_name='assert_device')


class MedicalDeviceSix8CateListView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin, SystemManagePermission)

    def get(self, req):
        """
        获取医疗器械类型列表
        """
        self.check_object_any_permissions(req, req.user)

        medical_device_six8_cate_list = MedicalDeviceSix8Cate.objects.get_medical_device_six8_cates()

        return resp.serialize_response(
            medical_device_six8_cate_list, results_name='medical_device_six8_cates')


class AssertDeviceView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    def put(self, req, device_id):
        """
        修改资产设备
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if req.data.get("performer_id"):
            self.get_object_or_404(req.data.get('performer_id'), Staff)
        if req.data.get("use_dept_id"):
            self.get_object_or_404(req.data.get("use_dept_id"), Department)
        if req.data.get('responsible_dept_id'):
            self.get_object_or_404(req.data.get('responsible_dept_id'), Department)
        if req.data.get('medical_device_cate_id'):
            self.get_object_or_404(req.data.get('medical_device_cate_id'), MedicalDeviceSix8Cate)
        if req.data.get('storage_place_id'):
            self.get_object_or_404(req.data.get('storage_place_id'), HospitalAddress)

        modifier = req.user.get_profile()
        form = AssertDeviceUpdateForm(req.data, modifier, assert_device)

        if not form.is_valid():
            return resp.failed(form.errors)
        updated_assert_device = form.save()
        if not updated_assert_device:
            return resp.failed('操作失败')
        return resp.serialize_response(updated_assert_device, results_name='assert_device')

    def get(self, req, device_id):
        """
        资产设备详情
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        assert_device = self.get_object_or_404(device_id, AssertDevice)

        return resp.serialize_response(assert_device, results_name='assert_device')

    def delete(self, req, device_id):
        """
        删除资产设备
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if not assert_device.deleted():
            return resp.failed('操作失败')
        return resp.ok('操作成功')


class AssertDeviceScrapView(BaseAPIView):
    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    def put(self, req, device_id):
        """
        资产设备报废处理
        """

        self.check_object_any_permissions(req, req.user.get_profile().organ)

        assert_device = self.get_object_or_404(device_id, AssertDevice)

        if not assert_device.assert_device_scrapped():
            return resp.failed('操作失败')

        return resp.serialize_response(assert_device, results_name='assert_device')


class AssertDeviceBatchUploadView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    @check_params_not_null(['cate'])
    def post(self, req):
        """
        资产设备的批量导入
        """

        self.check_object_any_permissions(req, req.user.get_profile().organ)
        file_obj = req.FILES.get('file')
        cate = req.data.get('cate')
        if cate not in dict(ASSERT_DEVICE_CATE_CHOICES):
            return resp.failed('资产医疗设备分类异常')
        if not file_obj:
            return resp.failed('请选择上传的Excel表格')

        if not file_obj.content_type == ARCHIVE['.xlsx']:
            return resp.failed('请上传Excel表格')
        success, result = ExcelBasedOXL.open_excel(file_obj)
        if not success:
            return resp.failed(result)
        if req.data.get('cate') == ASSERT_DEVICE_CATE_MEDICAL:
            head_dict = UPLOADED_MEDICAL_ASSERT_DEVICE_EXCEL_HEADER_DICT
        else:
            head_dict = UPLOADED_INFORMATION_ASSERT_DEVICE_EXCEL_HEADER_DICT
        is_success, ret = ExcelBasedOXL.read_excel(result, head_dict)

        if not is_success:
            return resp.failed(ret)
        logger.info(ret)
        form = AssertDeviceBatchUploadForm(ret, creator=req.user.get_profile(), cate=cate)
        if not form.is_valid():
            logger.info(form.errors)
            return resp.failed(form.errors)
        if not form.save():
            logger.info('导入失败')
            return resp.failed('导入失败')
        logger.info('导入成功')
        return resp.ok('导入成功')


class AssertDeviceAllocateView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    @check_id('use_dept_id')
    @check_params_not_null(['assert_device_ids'])
    def put(self, req):
        """
        资产设备调配操作（单个设备调配、多个设备调配）
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)

        assert_device_ids = get_id_list(req.data.get('assert_device_ids', '').strip())

        assert_devices = AssertDevice.objects.get_assert_device_by_ids(assert_device_ids)
        if len(assert_devices) < len(assert_device_ids):
            return resp.failed('请确认是否有不存在的资产设备信息')
        use_dept_id = req.data.get('use_dept_id')
        use_dept = self.get_object_or_404(use_dept_id, Department)
        result = AssertDevice.objects.update_assert_devices_use_dept(assert_devices, use_dept)
        if not result:
            return resp.failed('调配失败')
        return resp.serialize_response(result, results_name='assert_devices')


class MaintenancePlanCreateView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    @check_id('executor_id')
    @check_params_not_null(['title', 'storage_place_ids', 'type', 'start_date',
                            'expired_date', 'assert_device_ids'])
    def post(self, req):
        """
        新建设备维护单（维护单号自动生产）
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        executor = self.get_object_or_404(req.data.get('executor_id'), Staff)

        storage_place_ids = get_id_list(req.data.get('storage_place_ids', '').strip())
        storage_places = HospitalAddress.objects.get_hospital_address_by_ids(storage_place_ids)
        if len(storage_places) < len(storage_place_ids):
            return resp.failed('请确认是否有不存在的存储地点信息')

        assert_device_ids = get_id_list(req.data.get('assert_device_ids', '').strip())
        assert_devices = AssertDevice.objects.get_assert_device_by_ids(assert_device_ids)
        if len(assert_devices) < len(assert_device_ids):
            return resp.failed('请确认是否有不存在的资产设备信息')
        form = MaintenancePlanCreateForm(
            req.data, storage_places, assert_devices, executor, req.user.get_profile())
        if not form.is_valid():
            return resp.failed(form.errors)
        maintenance_plan = form.save()
        if not maintenance_plan:
            return resp.failed('创建失败')
        return resp.serialize_response(maintenance_plan, results_name='maintenance_plan')


class MaintenancePlanView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin, MaintenancePlanExecutePermission)

    def get(self, req, maintenance_plan_id):
        """
        设备维护计划详情
        :param req:
        :param maintenance_plan_id:
        :return:
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        maintenance_plan = self.get_object_or_404(maintenance_plan_id, MaintenancePlan)
        return resp.serialize_response(maintenance_plan, results_name='maintenance_plan')


class MaintenancePlanListView(BaseAPIView):

    permission_classes = (MaintenancePlanExecutePermission, HospitalStaffPermission,
                          AssertDeviceAdminPermission, IsHospSuperAdmin)

    def get(self, req):
        """
        资产设备维护计划列表
        搜索字段：
            search_key: 维护计划编号/维护计划名称
            status: 维护计划状态（DN: 已执行，NW: 未执行）
            period: 时间段（逾期、今天到期、三日内到期、一周内到期、一年内到期）
        """
        self.check_object_any_permissions(req, req.user.get_profile().organ)
        if req.GET.get('search_key', '').strip():
            if not req.GET.get('search_key', '').strip() not in dict(MAINTENANCE_PLAN_STATUS_CHOICES):
                return resp.failed('资产设备维护计划状态错误')
        if req.GET.get('period', '').strip():
            if not req.GET.get('period', '').strip() not in dict(MAINTENANCE_PLAN_EXPIRED_DATE_CHOICES):
                return resp.failed('截止时间段错误')

        maintenance_plans = MaintenancePlan.objects.get_maintenance_plan_list(
            search_key=req.GET.get('search_key', '').strip(),
            status=req.GET.get('status', '').strip(),
            period=req.GET.get('period', '').strip()
        )

        for role in req.user.get_roles():
            if role.codename in (ROLE_CODE_ASSERT_DEVICE_ADMIN, ROLE_CODE_HOSP_SUPER_ADMIN):
                return self.get_pages(
                    maintenance_plans, srl_cls_name='MaintenancePlanListSerializer',
                    results_name='maintenance_plans'
                )

        maintenance_plans = maintenance_plans.filter(executor=req.user.get_profile())

        return self.get_pages(
            maintenance_plans, srl_cls_name='MaintenancePlanListSerializer',
            results_name='maintenance_plans'
        )


class MaintenancePlanExecuteView(BaseAPIView):

    permission_classes = (MaintenancePlanExecutePermission, AssertDeviceAdminPermission, IsHospSuperAdmin)

    def put(self, req, maintenance_plan_id):
        """
        资产设备维护单执行操作
        """
        maintenance_plan = self.get_object_or_404(maintenance_plan_id, MaintenancePlan)
        self.check_object_any_permissions(req, maintenance_plan)

        if maintenance_plan.status == MAINTENANCE_PLAN_STATUS_DONE:
            return resp.failed('维护单已执行')
        result = req.data.get('result', '').strip()
        if not result:
            return resp.failed('请输入处理结果')
        success = maintenance_plan.change_status(result)

        if not success:
            return resp.failed('操作失败')
        return resp.ok('操作成功')


class FaultTypeListView(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin, SystemManagePermission)

    def get(self, req):
        queryset = FaultType.objects.all()
        return resp.serialize_response(queryset, srl_cls_name='FaultTypeSerializer', results_name='fault_types')


class RepairOrderCreateView(BaseAPIView):
    """
    提交报修单
    """
    permission_classes = (HospitalStaffPermission, )

    def post(self, req, ):
        self.check_object_any_permissions(req, None)
        form = RepairOrderCreateForm(req.user.get_profile(), req.data)
        if not form.is_valid():
            return resp.form_err(form.errors)
        success, repair_order = form.save()
        if not success:
            return resp.failed("操作失败")
        return resp.serialize_response(repair_order, results_name='repair_order',
                                       srl_cls_name='RepairOrderSerializer')


class RepairOrderView(BaseAPIView):

    permission_classes = (
        RepairOrderCreatorPermission, RepairOrderHandlePermission,
        RepairOrderDispatchPermission, IsHospSuperAdmin
    )

    def get(self, req, order_id):

        repair_order = self.get_object_or_404(order_id, RepairOrder)
        self.check_object_any_permissions(req, repair_order)
        repair_order_queryset = RepairOrderSerializer.setup_eager_loading(RepairOrder.objects.filter(id=order_id))

        return resp.serialize_response(repair_order_queryset.first(), results_name='repair_order',
                                       srl_cls_name='RepairOrderSerializer')

    def put(self, req, order_id):

        repair_order = self.get_object_or_404(order_id, RepairOrder)
        self.check_object_any_permissions(req, repair_order)
        action = req.data.get('action', '').strip()
        if not action or action not in dict(REPAIR_ORDER_OPERATION_CHOICES):
            return resp.failed('请求数据异常')
        """ 分派报销单"""
        if action == REPAIR_ORDER_OPERATION_DISPATCH:
            if not repair_order.status == REPAIR_ORDER_STATUS_SUBMITTED:
                return resp.failed('请求数据异常')
            form = RepairOrderDispatchForm(req.user.get_profile(), repair_order, req.data)
            if not form.is_valid():
                return resp.form_err(form.errors)
            new_order = form.save()
            if not new_order:
                return resp.failed('操作失败')

        """ 维修工处理报修单 """
        if action == REPAIR_ORDER_OPERATION_HANDLE:
            if not repair_order.status == REPAIR_ORDER_STATUS_DOING:
                return resp.failed('请求数据异常')
            file_list = list()
            if req.data.get('files'):
                files_data = req.data.get('files')
                file_form = FileBulkCreateOrUpdateForm(req.user, files_data, dict(FILE_CATE_CHOICES))
                if not file_form.is_valid():
                    return resp.failed(file_form.errors)
                file_list = file_form.save()
            form = RepairOrderHandleForm(req.user.get_profile(), repair_order, req.data, files=file_list)
            if not form.is_valid():
                return resp.form_err(form.errors)
            new_order = form.save()
            if not new_order:
                return resp.failed('操作失败')

        """ 评论此次报修 """
        if action == REPAIR_ORDER_OPERATION_COMMENT:
            if not repair_order.status == REPAIR_ORDER_STATUS_DONE:
                return resp.failed('请求数据异常')
            form = RepairOrderCommentForm(req.user.get_profile(), repair_order, req.data)
            if not form.is_valid():
                return resp.form_err(form.errors)
            new_order = form.save()
            if not new_order:
                return resp.failed('操作失败')
        queryset = RepairOrderSerializer.setup_eager_loading(RepairOrder.objects.filter(id=order_id))
        return resp.serialize_response(
            queryset.first(), results_name='repair_order', srl_cls_name='RepairOrderSerializer'
        )


class RepairOrderListView(BaseAPIView):

    permission_classes = (
         RepairOrderDispatchPermission, IsHospSuperAdmin, HospitalStaffPermission,
    )

    def get_queryset(self):
        return RepairOrder.objects.all().order_by('-created_time')

    def get(self, req):
        self.check_objects_any_permissions(req, None)
        action = req.GET.get('action', '').strip()
        status = req.GET.get('status', '').strip()
        search = req.GET.get('search', '').strip()

        if action not in ORDERS_ACTION_CHOICES:
            return resp.failed('请求数据异常')
        queryset = self.get_queryset()
        if action == MY_REPAIR_ORDERS:
            queryset = queryset.filter(creator=req.user.get_profile())
        if action == TO_DISPATCH_ORDERS:
            queryset = queryset.filter(status=REPAIR_ORDER_STATUS_SUBMITTED)
        if action == MY_MAINTAIN_ORDERS:
            queryset = queryset.filter(maintainer=req.user.get_profile())
        if action == ALL_ORDERS:
            queryset = queryset
        if status:
            if status not in dict(REPAIR_ORDER_STATUS_CHOICES):
                return resp.failed("请求数据异常")
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(fault_type__title__contains=search) | Q(order_no__contains=search) |
                Q(creator__name__contains=search)
            )
        return self.get_pages(queryset, srl_cls_name='RepairOrderSerializer', results_name='repair_orders')


class RepairOrderRecordListView(BaseAPIView):

    permission_classes = (
        RepairOrderCreatorPermission, RepairOrderHandlePermission,
        RepairOrderDispatchPermission, IsHospSuperAdmin
    )

    def get(self, req, order_id):
        order = self.get_object_or_404(order_id, RepairOrder)
        self.check_object_any_permissions(req, order)
        record_query_set = order.get_repair_order_records().order_by('-created_time')
        return resp.serialize_response(
            record_query_set, results_name='repair_order_records', srl_cls_name='RepairOrderRecordSerializer'
        )


class FaultSolutionCreateView(BaseAPIView):

    permission_classes = (KnowledgeManagePermission, IsHospSuperAdmin)

    def post(self, req):
        self.check_object_any_permissions(req, None)
        file_list = list()
        if req.data.get('files'):
            files_data = req.data.get('files')
            file_form = FileBulkCreateOrUpdateForm(req.user, files_data, dict(FILE_CATE_CHOICES))
            if not file_form.is_valid():
                return resp.failed(file_form.errors)
            file_list = file_form.save()
        form = FaultSolutionCreateForm(req.user.get_profile(), req.data, files=file_list)
        if not form.is_valid():
            return resp.failed(form.errors)
        fault_solution = form.save()
        if not fault_solution:
            return resp.failed('操作失败')
        return resp.serialize_response(fault_solution, 'fault_solution', srl_cls_name='FaultSolutionSerializer')


class FaultSolutionView(BaseAPIView):

    @permission_classes((HospitalStaffPermission, ))
    def get(self, req, fault_solution_id):
        self.check_object_any_permissions(req, None)
        fault_solution = self.get_object_or_404(fault_solution_id, FaultSolution)
        queryset = FaultSolutionSerializer.setup_eager_loading(
            FaultSolution.objects.filter(id=fault_solution_id)
        )
        return resp.serialize_response(
            queryset.first(), results_name='fault_solution', srl_cls_name='FaultSolutionSerializer'
        )

    @permission_classes((KnowledgeManagePermission, IsHospSuperAdmin))
    def put(self, req):
        self.check_object_any_permissions(req, None)
        pass

    def delete(self, req):
        pass


class FaultSolutionBatchDeleteView(BaseAPIView):

    permission_classes = (KnowledgeManagePermission, IsHospSuperAdmin)

    def post(self, req):
        self.check_object_any_permissions(req, None)

        ids_str = req.data.get('ids')
        fs_ids = list()
        try:
            for id_str in ids_str:
                fs_ids.append(int(id_str))
            queryset = FaultSolution.objects.filter(id__in=fs_ids)
            count = queryset.count()
            if count < len(fs_ids):
                return resp.form_err({'ids': 'id为空或数据错误'})
            FaultSolution.objects.clear_cache(queryset)
            queryset.delete()
            return resp.ok('操作成功')
        except ValueError as ve:
            logger.exception(ve)
            return resp.form_err({'ids': 'id为空或数据错误'})
        except Exception as exc:
            logger.exception(exc)
            return resp.failed('操作失败')


class FaultSolutionListView(BaseAPIView):

    permission_classes = (HospitalStaffPermission, IsHospSuperAdmin)

    def get(self, req):
        self.check_object_any_permissions(req, None)
        search = req.GET.get('search', '').strip()

        queryset = FaultSolution.objects.all().order_by('id')

        if search:
            queryset = queryset.filter(
                Q(fault_type__title__contains=search) | Q(title__contains=search)
            )
        return self.get_pages(queryset, results_name='fault_solutions', srl_cls_name='FaultSolutionSerializer')


class FaultSolutionsImportView(BaseAPIView):

    permission_classes = (KnowledgeManagePermission, IsHospSuperAdmin)

    @check_params_not_null(['file'])
    def post(self, req):
        """
         批量导入故障问题解决方案
         :param req:
         :return:
         """
        self.check_object_any_permissions(req, None)

        file_obj = req.FILES.get('file')
        if not file_obj:
            return resp.failed('请选择要上传的文件')

        if not ARCHIVE['.xlsx'] == file_obj.content_type:
            return resp.failed('导入文件不是Excel文件，请检查')

        # 将文件存放到服务器
        # import os
        # file_server_path = open(os.path.join('/media/', '', file_obj.name), 'wb')
        # file = open('file_server_path', 'wb')
        # file_info = files.upload_file(file_obj, DOC_UPLOAD_BASE_DIR)

        is_success, ret = ExcelBasedOXL.open_excel(file_obj)
        if not is_success:
            return resp.failed(ret)
        success, result = ExcelBasedOXL.read_excel(ret, UPLOADED_FS_EXCEL_HEAD_DICT)
        ExcelBasedOXL.close(ret)
        if not success:
            return resp.failed(result)

        form = FaultSolutionsImportForm(req.user.get_profile(), result)
        if not form.is_valid():
            return resp.form_err(form.errors)

        return resp.ok('导入成功') if form.save() else resp.failed('导入失败')


class FaultSolutionsExportView(BaseAPIView):

    permission_classes = (KnowledgeManagePermission, IsHospSuperAdmin)

    def post(self, req):
        self.check_object_any_permissions(req, None)

        search = req.GET.get('search', '').strip()

        queryset = FaultSolution.objects.all()

        if search:
            queryset = queryset.filter(
                Q(fault_type__title__contains=search) | Q(title__contains=search)
            )
        records = list()
        for item in queryset:
            records.append([item.title, item.solution, item.fault_type.title,  item.creator.name, times.datetime_to_str(item.created_time)])
        header_rows = [['标题', '解决方案', '故障类型', '贡献人', '创建时间'], ]
        name = 'operation-maintenance-knowledge'
        excel_file_name, file_path = ExcelBasedOXL.export_excel(
            DOC_DOWNLOAD_BASE_DIR,
            name,
            [records],
            ['知识库-故障问题解决方案', ],
            header_rows
        )
        from django.http import StreamingHttpResponse
        import os
        path = os.path.join(settings.MEDIA_ROOT, file_path)
        response = StreamingHttpResponse(file_read_iterator(path))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format(u'%s' % excel_file_name)
        return response


class OperationMaintenanceReportView(BaseAPIView):
    """
    维修相关统计报表
    """

    permission_classes = (IsHospSuperAdmin, HospGlobalReportAssessPermission)
    queryset = RepairOrder.objects.all()

    def get(self, req):
        self.check_object_any_permissions(req, None)

        # 校验日期格式
        if not times.is_valid_date(req.GET.get('start_date', '')) or not times.is_valid_date(req.GET.get('expired_date', '')):
            return resp.form_err({'start_date or expired_date': '开始日期/截止日期为空或数据错误'})

        start_date = '%s %s' % (req.GET.get('start_date', times.now().strftime('%Y-01-01')), '00:00:00.000000')
        expired_date = '%s %s' % (req.GET.get('end_date', times.now().strftime('%Y-12-31')), '23:59:59.999999')

        # 已处理维修总数、维修申请总数、维修完成率
        rp_order_nums_status_queryset = self.queryset.filter(created_time__range=(start_date, expired_date)) \
            .values('status') \
            .annotate(nums=Count('id', distinct=True))

        # 按故障类型统计报修单数量
        rp_order_nums_fault_type_queryset = self.queryset.filter(created_time__range=(start_date, expired_date)) \
            .annotate(fault_type_title=F('fault_type__title')) \
            .values('fault_type_title') \
            .annotate(nums=Count('id', distinct=True)).order_by('-nums')

        # 科室故障申请Top3
        rp_order_nums_top_dept_queryset = self.queryset.filter(created_time__range=(start_date, expired_date))\
            .annotate(dept=F('applicant__dept__name'))\
            .values('dept')\
            .annotate(nums=Count('id', distinct=True)).order_by('-nums')[0:3]

        data = {
            'rp_order_nums_status': list(rp_order_nums_status_queryset),
            'rp_order_nums_fault_type': list(rp_order_nums_fault_type_queryset),
            'rp_order_nums_top_dept': list(rp_order_nums_top_dept_queryset),
        }
        return resp.ok('ok', data)


class AssertDeviceBatchUploadViewTest(BaseAPIView):

    permission_classes = (AssertDeviceAdminPermission, IsHospSuperAdmin)

    @check_params_not_null(['cate'])
    def post(self, req):
        """
        资产设备的批量导入
        """

        self.check_object_any_permissions(req, req.user.get_profile().organ)
        file_obj = req.FILES.get('file')
        cate = req.data.get('cate')
        if cate not in dict(ASSERT_DEVICE_CATE_CHOICES):
            return resp.failed('资产医疗设备分类异常')
        if not file_obj:
            return resp.failed('请选择上传的Excel表格')

        if not file_obj.content_type == ARCHIVE['.xlsx']:
            return resp.failed('请上传Excel表格')
        success, result = ExcelBasedOXL.open_excel(file_obj)
        if not success:
            return resp.failed(result)
        if req.data.get('cate') == ASSERT_DEVICE_CATE_MEDICAL:
            head_dict = UPLOADED_MEDICAL_ASSERT_DEVICE_EXCEL_HEADER_DICT
        else:
            head_dict = UPLOADED_INFORMATION_ASSERT_DEVICE_EXCEL_HEADER_DICT

        sheet = result.worksheets[0]
        max_row = sheet.max_row
        # 校验表头信息是否一致

        for cell in list(sheet.rows)[0]:
            if cell.value not in dict(zip(head_dict.values(), head_dict.keys())):
                return resp.failed('表单的表头数据和指定的标准不一致')
        import datetime
        # 封装sheet数据
        sheet_data_list = []
        for i in range(1, max_row):
            row_list = []
            for cell in list(sheet.rows)[i]:
                if isinstance(cell.value, datetime.datetime):
                    value = cell.value.strftime('%Y-%m-%d')
                else:
                    value = cell.value
                row_list.append(value)
            sheet_data_list.append(row_list)
        logger.info('===========================')
        logger.info(sheet_data_list)

        keys = head_dict.keys()
        logger.info('============================')
        logger.info(keys)

        # 封装assert_device数据
        assert_device_data_list = []
        for data in sheet_data_list:
            assert_device = dict(zip(keys, data))
            assert_device_data_list.append(assert_device)
        logger.info('=============================')
        logger.info(assert_device_data_list)

        form = AssertDeviceBatchUploadForm(assert_device_data_list, creator=req.user.get_profile(), cate=cate)
        if not form.is_valid():
            logger.info(form.errors)
            return resp.failed(form.errors)
        if not form.save():
            logger.info('导入失败')
            return resp.failed('导入失败')
        return resp.ok('导入成功')