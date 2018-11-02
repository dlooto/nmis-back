
import logging


from django.db.models.signals import post_save
from django.dispatch import receiver

from nmis.devices.consts import REPAIR_ORDER_OPERATION_SUBMIT, REPAIR_ORDER_OPERATION_CHOICES, \
    REPAIR_ORDER_STATUS_DOING, REPAIR_ORDER_OPERATION_DISPATCH, REPAIR_ORDER_STATUS_DONE, REPAIR_ORDER_OPERATION_HANDLE, \
    REPAIR_ORDER_OPERATION_COMMENT, REPAIR_ORDER_STATUS_CLOSED
from nmis.devices.models import RepairOrder, RepairOrderRecord

logger = logging.getLogger(__name__)


@receiver(post_save, sender=RepairOrder)
def gen_operation_record(sender, **kwargs):
    repair_order = kwargs.get('instance')
    created = kwargs.get('created')
    creator = repair_order.creator
    if created:
        msg_content = '%s(%s)%s%s(%s)' % (
            creator.name, creator.dept.name,
            dict(REPAIR_ORDER_OPERATION_CHOICES).get(REPAIR_ORDER_OPERATION_SUBMIT),
            '了报修单', repair_order.order_no,
        )
        RepairOrderRecord.objects.create(
            repair_order=repair_order, operation=REPAIR_ORDER_OPERATION_SUBMIT,
            operator=creator, msg_content=msg_content
        )
    if repair_order.status == REPAIR_ORDER_STATUS_DOING:
        operator = repair_order.modifier
        maintainer = repair_order.maintainer
        msg_content = '%s(%s)%s(%s)%s%s(%s)' % (
            operator.name, operator.dept.name, '已分派了报修单', repair_order.order_no,
            '给', maintainer.name, maintainer.dept.name,
        )
        RepairOrderRecord.objects.create(
            repair_order=repair_order, operation=REPAIR_ORDER_OPERATION_DISPATCH,
            operator=operator, msg_content=msg_content, receiver=maintainer
        )
    if repair_order.status == REPAIR_ORDER_STATUS_DONE:
        operator = repair_order.modifier
        msg_content = '%s(%s)%s(%s)' % (
            operator.name, operator.dept.name, '已处理完报修单', repair_order.order_no,
        )
        RepairOrderRecord.objects.create(
            repair_order=repair_order, operation=REPAIR_ORDER_OPERATION_HANDLE,
            operator=operator, msg_content=msg_content
        )
    if repair_order.status == REPAIR_ORDER_STATUS_CLOSED and repair_order.comment_time:
        operator = repair_order.modifier
        msg_content = '%s(%s)%s(%s)' % (
            operator.name, operator.dept.name, '评论了报修单', repair_order.order_no,
        )
        RepairOrderRecord.objects.create(
            repair_order=repair_order, operation=REPAIR_ORDER_OPERATION_COMMENT,
            operator=operator, msg_content=msg_content
        )
