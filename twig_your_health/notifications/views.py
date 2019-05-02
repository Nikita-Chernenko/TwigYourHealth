from django.conf import settings
from django.http import JsonResponse

from accounts.models import User
from notifications.models import Notification


def mark_read(request):
    Notification.objects.filter(owner=request.user).update(seen=True)
    return JsonResponse({'success': True})


def send_message():
    pb = settings.pb
    device = pb.get_device('Xiaomi Redmi Note 4')
    notifications = Notification.objects.filter(important=True, sent=False)
    for n in notifications:
        push = pb.push_sms(device, n.owner.phone, n.text)
        n.sent = True
        n.save()


def add_message(message: str, owner: User, important: bool = False):
    Notification.objects.create(text=message, owner=owner, important=important)
