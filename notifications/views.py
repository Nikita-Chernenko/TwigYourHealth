from django.shortcuts import render
from pushbullet import Pushbullet

from TwigYourHealth.settings import pb
from notifications.models import Notification


def send_message():
    device = pb.get_device('Xiaomi Redmi Note 4')
    notification = Notification.objects.first()
    push = pb.push_sms(device, notification.owner.phone, notification.text)
