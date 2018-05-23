import datetime
import json
from copy import deepcopy

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers import serialize
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.utils.dateparse import parse_date, parse_datetime
from django.views.decorators.http import require_http_methods

from communication.forms import MessageForm
from communication.models import Chat, Message
from communication.utils import _user_belong_to_chat

MESSAGE_CREATE = 'message_create'
MESSAGE_DELETE = 'message_delete'
MESSAGE_UPDATE = 'message_update'


def chat_retrieve(request, pk):
    chat = get_object_or_404(Chat, pk=pk)
    if not _user_belong_to_chat(request.user, chat):
        JsonResponse("User doesn't belong to chat", status=403)
    chat = serialize(queryset=[chat], format='json')
    return JsonResponse(data=chat, safe=False)


def message_list(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)
    messages = chat.message_set.all()
    messages = json.loads(serialize(queryset=messages, format='json'))
    for m in messages:
        m['fields']['timestamp'] = parse_datetime(m['fields']['timestamp']).strftime('%H:%M')
    messages = json.dumps(messages)
    return JsonResponse(data=messages, safe=False)


@require_http_methods(['POST'])
def message_create_update(request, pk=None):
    data = deepcopy(request.POST)
    data['author'] = request.user.id
    form = MessageForm(data, instance=pk)
    if form.is_valid():
        message = form.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat-{message.chat.id}',
            {
                "type": "chat.message.update" if pk else "chat.message",
                "chat_id": message.chat.id,
                "user_id": request.user.id,
                "patient_read": message.patient_read,
                "doctor_read": message.doctor_read,
                "text": message.text,
                "timestamp": message.timestamp.strftime('%H:%M'),
                "action": MESSAGE_CREATE if pk else MESSAGE_CREATE,
                "message_id": message.id
            }
        )
        return JsonResponse(data='', status=200 if pk else 201, safe=False)
    return JsonResponse(data=form.errors, status=400, safe=False)


@require_http_methods(['POST'])
def message_delete(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.author == request.user:
        message.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat-{message.chat.id}',
            {
                "type": "chat.message.delete",
                "message_id": message.chat.id,
                "action": MESSAGE_DELETE
            }
        )
    return JsonResponse('')


def message_search(request, text, chat_id=None):
    user = request.user
    if chat_id:
        chat = get_object_or_404(Chat, pk=chat_id)
        if not _user_belong_to_chat(request.user, chat):
            JsonResponse("User doesn't belong to chat", status=403)

        chats = [chat_id]
    else:
        if request.user.is_doctor:
            chats = Chat.objects.filter(doctor=request.user.doctor).values_list('id', flat=True)
        elif request.user.is_patient:
            chats = Chat.objects.filter(patient=request.user.patient).values_list('id', flat=True)
        else:
            return Http404
    messages = Message.objects.filter(chat_id__in=chats, text__icontains=text).select_related('chat')
    messages = serialize(queryset=messages, format='json')
    return JsonResponse(messages, safe=False)
