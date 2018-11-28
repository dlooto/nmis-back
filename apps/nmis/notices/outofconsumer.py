import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# 外部调用channels的send方法
channels_layer = get_channel_layer()


# 服务端向项目分配者发送新建项目申请
def send_messages(staffs, message):
    """
    :param staffs:  拥有项目分配者权限员工集合
    :param message: 推送消息
    :return:
    """
    if staffs:
        for staff in staffs:
            async_to_sync(channels_layer.group_send)(
                str(staff.id),
                {
                    "type": "send.messages",
                    "message": message

                 }
            )


# 项目分配者驳回项目操作成功后给当前项目申请者发送项目被驳回消息
def send_project_operation_message(staff, message):
    """
    :param staff: 被驳回的项目
    :param message: 操作后向客户端发送的消息
    """
    async_to_sync(channels_layer.group_send)(
        str(staff.id),
        {
            "type": "send.messages",
            "message": message

        }
    )


# 新建设备维修成功后向维修任务分配者推送消息
def send_repair_order_message(staffs, message):
    if staffs:

        for staff in staffs:
            async_to_sync(channels_layer.group_send)(
                str(staff.id),
                {
                    "type": "send.messages",
                    "message": message
                 }
            )


# 维修任务分配者分派维修单成功后向维修人员推送消息
def send_repair_order_dispatched_message(staff, message):
    async_to_sync(channels_layer.group_send)(
        str(staff.id),
        {
            "type": "send.messages",
            "message": message
        }
    )