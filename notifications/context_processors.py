from notifications.models import Notification


def notifications(request):
    return {'notifications': Notification.objects.filter(owner=request.user, seen=False)}
