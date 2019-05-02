from django.contrib.auth.backends import ModelBackend
from annoying.functions import get_object_or_None
from accounts.models import User

class EmailPhoneUsernameBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            pass

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_object_or_None(User, username=username) or \
               get_object_or_None(User, email=username) or \
               get_object_or_None(User, phone=username)
        print(user)
        if user and user.check_password(password):
            return user
