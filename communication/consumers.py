from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.shortcuts import get_object_or_404

from accounts.models import User, Relationships
from communication.models import Chat


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        self.user = user
        if not user.is_patient and not user.is_doctor:
            self.close()
            return
        self.accept()
        pk = self.scope['url_route']['kwargs']['user_id']
        if user.is_doctor:
            patient_user, doctor_user = get_object_or_404(User, pk=pk), user
        else:
            doctor_user, patient_user = get_object_or_404(User, pk=pk), user

        if not Relationships.objects.filter(patient=patient_user.patient, doctor=doctor_user.doctor).exists():
            self.close()
            return
        chat, _ = Chat.objects.get_or_create(patient=patient_user.patient, doctor=doctor_user.doctor)
        self.patient_user = patient_user
        self.doctor_user = doctor_user
        self.chat_id = chat.id
        async_to_sync(self.channel_layer.group_add)(f"chat-{chat.id}", self.channel_name)

        # def receive_json(self, content, **kwargs):
        #     chat_id = self.chat_id
        #     user_id = self.user.id
        #     async_to_sync(self.channel_layer.group_send)(
        #         f'chat-{chat_id}',
        #         {
        #             "type": "chat.message",
        #             "chat_id": chat_id,
        #             "user_id": user_id,
        #             "message": content['text'],
        #         }
        #     )
        #     super(ChatConsumer, self).receive_json(content, **kwargs)

    def chat_message(self, event):
        self.send_json(
            event
        )

    def chat_message_update(self, event):
        self.send_json(
            event
        )

    def chat_message_delete(self, event):
        self.send_json(
            event
        )

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(f"chat-{self.chat_id}", self.channel_name)


class CallConsumer(JsonWebsocketConsumer):
    def connect(self):
        user = self.scope['user']
        self.user = user
        if not user.is_authenticated or not user.is_patient and not user.is_doctor:
            self.close()
            return
        self.accept()
        async_to_sync(self.channel_layer.group_add)(f"user-{user.id}", self.channel_name)

    def call_request(self, event):
        self.send_json(event)

    def call_accept(self, event):
        self.send_json(event)

    def call_decline(self, event):
        self.send_json(event)

    def call_end(self, event):
        self.send_json(event)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(f"user-{self.user.id}", self.channel_name)
