import datetime
import json
import uuid
from copy import deepcopy

from annoying.functions import get_object_or_None
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.serializers import serialize
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_http_methods, require_POST

from accounts.models import Doctor, Patient, User
from communication.forms import MessageForm
from communication.models import Chat, Message, CallEntity
from communication.utils import _user_belong_to_chat
from utils.checks import has_relationships

MESSAGE_CREATE = 'message_create'
MESSAGE_DELETE = 'message_delete'
MESSAGE_UPDATE = 'message_update'

CALL_REQUEST = 'call_request'
CALL_ACCEPT = 'call_accept'
CALL_DECLINE = 'call_decline'
CALL_END = 'call_end'


def chat_create(request):
    doctor_pk = request.POST['doctor']
    patient_pk = request.POST['patient']
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    patient = get_object_or_404(Patient, pk=patient_pk)
    Chat.objects.get_or_create(patient=patient, doctor=doctor)
    return JsonResponse({'success': True})


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


@require_POST
def call_request(request, with_id):
    user_from = request.user
    user_to = get_object_or_404(User, pk=with_id)
    if user_from.is_doctor and user_to.is_patient:
        doctor, patient = user_from.doctor, user_to.patient
    elif user_from.is_patient and user_to.is_doctor:
        patient, doctor = user_from.patient, user_to.doctor
    else:
        return HttpResponseForbidden("Available only between patient an doctor")
    if not has_relationships(doctor.pk, patient.pk):
        return HttpResponseForbidden("You have no connection with the user")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user-{user_to.id}',
        {
            "type": "call.request",
            "user_id": user_from.id,
            "action": CALL_REQUEST,
        }
    )
    return JsonResponse({})


@require_POST
def call_accept(request, with_id):
    user_from = request.user
    user_to = get_object_or_404(User, pk=with_id)
    if user_from.is_doctor and user_to.is_patient:
        doctor, patient = user_from.doctor, user_to.patient
    elif user_from.is_patient and user_to.is_doctor:
        patient, doctor = user_from.patient, user_to.doctor
    else:
        return HttpResponseForbidden("Available only between patient an doctor")
    if not has_relationships(doctor.pk, patient.pk):
        return HttpResponseForbidden("You have no connection with the user")
    room_name = str(uuid.uuid4())
    if doctor.is_private:
        CallEntity.objects.create(doctor=doctor, patient=patient, room=room_name,
                                  start=datetime.datetime.now(), end=datetime.datetime.now())

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user-{user_to.id}',
        {
            "type": "call.accept",
            "user_id": user_from.id,
            "room": room_name,
            "action": CALL_ACCEPT,
        }
    )
    return JsonResponse({'room': room_name})


@require_POST
def call_decline(request, with_id):
    user_from = request.user
    user_to = get_object_or_404(User, pk=with_id)
    if user_from.is_doctor and user_to.is_patient:
        doctor, patient = user_from.doctor, user_to.patient
    elif user_from.is_patient and user_to.is_doctor:
        patient, doctor = user_from.patient, user_to.doctor
    else:
        return HttpResponseForbidden("Available only between patient an doctor")
    if not has_relationships(doctor.pk, patient.pk):
        return HttpResponseForbidden("You have no connection with the user")
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user-{user_to.id}',
        {
            "type": "call.decline",
            "user_id": user_from.id,
            "action": CALL_DECLINE,
        }
    )
    return JsonResponse({'success': True})


@require_POST
def call_end(request, with_id, room_name):
    user_from = request.user
    user_to = get_object_or_404(User, pk=with_id)
    if user_from.is_doctor and user_to.is_patient:
        doctor, patient = user_from.doctor, user_to.patient
    elif user_from.is_patient and user_to.is_doctor:
        patient, doctor = user_from.patient, user_to.doctor
    else:
        return HttpResponseForbidden("Available only between patient an doctor")
    if not has_relationships(doctor.pk, patient.pk):
        return HttpResponseForbidden("You have no connection with the user")
    if doctor.is_private:
        call_entity = get_object_or_None(CallEntity, room=room_name)
        if call_entity:
            call_entity.end = datetime.datetime.now()
            call_entity.save()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'user-{user_to.id}',
        {
            "type": "call.end",
            "user_id": user_from.id,
            "room": room_name,
            "action": CALL_END,
        }
    )
    return JsonResponse({'success': True})
