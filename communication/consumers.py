from asgiref.sync import async_to_sync, AsyncToSync
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
from django.shortcuts import get_object_or_404

from accounts.models import User
from communication.models import Chat


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        self.user = user
        #         TODO add relationships check
        if not user.is_patient and not user.is_doctor:
            self.close()
            return
        self.accept()

        if user.is_doctor:
            patient_user, doctor_user = get_object_or_404(User, pk=self.scope['url_route']['kwargs']['user_id']), user
        else:
            doctor_user, patient_user = get_object_or_404(User, pk=self.scope['url_route']['kwargs']['user_id']), user

        chat, _ = Chat.objects.get_or_create(patient=patient_user.patient, doctor=doctor_user.doctor)
        self.patient_user = patient_user
        self.doctor_user = doctor_user
        self.chat_id = chat.id
        async_to_sync(self.channel_layer.group_add)(f"chat-{chat.id}", self.channel_name)

    def receive_json(self, content, **kwargs):
        chat_id = self.chat_id
        user_id = self.user.id
        async_to_sync(self.channel_layer.group_send)(
            f'chat-{chat_id}',
            {
                "type": "chat.message",
                "chat_id": chat_id,
                "user_id": user_id,
                "message": content['text'],
            }
        )
        super(ChatConsumer, self).receive_json(content, **kwargs)

    def chat_message(self, event):
        self.send_json(
            event
        )
