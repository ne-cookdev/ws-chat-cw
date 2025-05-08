import base64
import json
import secrets
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile

from accounts.models import MyUser
from .models import Message, Conversation
from .serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        conversation = Conversation.objects.get(id=int(self.room_name))
        messages = Message.objects.filter(conversation_id=conversation).exclude(sender=self.scope['user'])
        for message in messages:
            message.is_read = True
            message.save()

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        conversation = Conversation.objects.get(id=int(self.room_name))
        messages = Message.objects.filter(conversation_id=conversation).exclude(sender=self.scope['user'])
        for message in messages:
            message.is_read = True
            message.save()
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # parse the json data into dictionary object
        text_data_json = json.loads(text_data)

        # Send message to room group
        chat_type = {"type": "chat_message"}
        conversation = Conversation.objects.get(id=int(self.room_name))
        sender = self.scope['user']
        message, attachment = (
            text_data_json["message"],
            text_data_json.get("attachment"),
        )
        if attachment:
            file_str, file_ext = attachment["data"], attachment["format"]

            file_data = ContentFile(
                base64.b64decode(file_str), name=f"{secrets.token_hex(8)}.{file_ext}"
            )
            _message = Message.objects.create(
                sender=sender,
                attachment=file_data,
                text=message,
                conversation_id=conversation,
            )
        else:
            _message = Message.objects.create(
                sender=sender,
                text=message,
                conversation_id=conversation,
            )
        text_data_json['_message'] = _message
        return_dict = {**chat_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            return_dict,
        )

    # Receive message from room group
    def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")

        serializer = MessageSerializer(instance=text_data_json['_message'])
        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                serializer.data
            )
        )
