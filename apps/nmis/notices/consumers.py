from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import asgiref
import json


class ChatConsumer(WebsocketConsumer):
    # 建立连接
    def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['staff_id']
        self.room_group_name = self.scope['url_route']['kwargs']['staff_id']

        # 加入连接组
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    # 关闭连接
    def disconnect(self, close_code):
        # 退出组
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # 接收客户端发送的消息
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['messages']

        # 发送消息
        asgiref.sync.async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # 接收消息组传进的消息
    def chat_message(self, event):
        message = event['messages']
        # 发送消息到客户端

        self.send(text_data=json.dumps({
            'message': message
        }))

    def send_messages(self, event):

        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

