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