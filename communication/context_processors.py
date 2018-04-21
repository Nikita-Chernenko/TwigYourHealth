from communication.models import Chat


def chats(request):
    user = request.user
    if user.is_authenticated and user.is_doctor:
        chats = Chat.objects.filter(doctor=user.doctor)
    elif user.is_authenticated and user.is_patient:
        chats = Chat.objects.filter(patient=user.patient)
    else:
        return {}
    return {'chats': chats}
