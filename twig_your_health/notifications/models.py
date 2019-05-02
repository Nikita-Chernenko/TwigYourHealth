from django.db import models

# Create your models here.
from accounts.models import User


class Notification(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    seen = models.BooleanField(default=False)
    important = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.owner} {self.text} {self.seen}'
