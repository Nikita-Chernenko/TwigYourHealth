from django.db import models


# Create your models here.
from accounts.models import User


class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    seen = models.BooleanField(default=False)
