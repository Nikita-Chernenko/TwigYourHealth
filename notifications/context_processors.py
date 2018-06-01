from notifications.models import Notification


def notifications(request):
    if request.user.is_authenticated:
        n = list(Notification.objects.filter(owner=request.user, seen=False))
        n_count = len(n)
        if n_count < 5:
            n.extend(list(Notification.objects.filter(owner=request.user)
                          .exclude(seen=False).order_by('-id')[:5 - n_count]))
        return {'notifications': n, 'new_notifications_count': n_count}
    return {}
