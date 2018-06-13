from communication.models import ChatEntity, Message, Chat
from timetables.models import Visit
from time import gmtime, strftime
from payments.models import Order


def visit_billing():
    today = strftime("%Y-%m-%d", gmtime())
    visits = Visit.objects.filter(shift__day__lte=today)
    for visit in visits:
        if visit.orders.count() == 0:
            order = Order(interaction=visit)
            order.save()
            visit.orders.add(order)


def chat_billing():
    for chat in Chat.objects.all():
        chat_entity = ChatEntity.objects.filter(doctor=chat.doctor, patient=chat.patient).first()
        if chat_entity is not None:
            timestamp = ChatEntity.objects \
                .filter(doctor=chat.doctor, patient=chat.patient) \
                .latest('timestamp')\
                .timestamp
            messages = Message.objects.filter(chat=chat, timestamp__gt=timestamp)
        else:
            messages = Message.objects.filter(chat=chat)

        new_chat_entity = ChatEntity(patient=chat.patient, doctor=chat.doctor, hours=1)
        new_chat_entity.save()
        for message in messages:
            new_chat_entity.messages.add(message)
        new_chat_entity.save(force_insert=True)
        order = Order(interaction=new_chat_entity)
        order.save()
