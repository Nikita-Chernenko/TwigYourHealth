from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from accounts.models import Doctor, Patient, User


class CallEntity(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, verbose_name='doctor')
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='patient')
    orders = GenericRelation('payments.Order', on_delete=models.CASCADE)
    room = models.CharField('room name', max_length=256, null=True)
    start = models.DateTimeField('start')
    end = models.DateTimeField('end')

    def __init__(self, *args, **kwargs):
        super(CallEntity, self).__init__(*args, **kwargs)
        self.__original_start = self.start
        self.__original_end = self.end

    def __str__(self):
        return f'{self.doctor} {self.patient} {self.start} {self.end}'

    def clean(self):
        if self.start and self.end:
            start, end = self.start, self.end
            start_changed, end_changed = self.start != self.__original_start, self.end != self.__original_end

            if (start_changed or end_changed) and self.objects.filter(
                    (Q(start__lte=start) & Q(end__gte=start)) |
                    (Q(end__gte=end) & Q(start__lte=end)) |
                    (Q(start__gte=start) & Q(end__lte=end))).exists():
                raise ValidationError(f'{self._meta.model_name} for this time already exists')


class Chat(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)

    class Meta:
        unique_together = [['patient', 'doctor']]

    def __str__(self):
        return f'{self.patient} {self.doctor}'

    @property
    def last_message(self):
        return self.message_set.latest()


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('timestamp', auto_now=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    doctor_read = models.BooleanField(default=False)
    patient_read = models.BooleanField(default=False)
    text = models.TextField('text')

    class Meta:
        ordering = ['chat', 'timestamp']
        get_latest_by = ['timestamp']

    def __str__(self):
        return f'{self.chat} {self.text}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.author:
            if self.author.is_patient:
                self.patient_read = True
            elif self.author.is_doctor:
                self.doctor_read = True
        super(Message, self).save(force_insert, force_update, using, update_fields)

    def clean(self):
        if hasattr(self, 'author') and hasattr(self, 'chat') \
                and (self.author.is_patient and self.author.patient != self.chat.patient or
                     self.author.is_doctor and self.author.doctor != self.chat.doctor):
            raise ValidationError("User doesn't belong to chat")


class ChatEntity(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, verbose_name='doctor')
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='patient')
    orders = GenericRelation('payments.Order', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    messages = models.ManyToManyField(Message)
    hours = models.FloatField('sum of minutes spent on chat')

    class Meta:
        ordering = ['timestamp']
        get_latest_by = ['timestamp']

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.messages.exists():
            minutes = 0
            for message in self.messages.all():
                if hasattr(message.author, 'doctor'):
                    minutes += len(message.text) / 50
                elif hasattr(message.author, 'patient'):
                    minutes += len(message.text) / 100
            self.hours = minutes / 60
        super(ChatEntity, self).save(force_insert, force_update, using, update_fields)

    def clean(self):
        if self.messages.exists():
            if self.id:
                last_entity = ChatEntity.objects.filter(~Q(pk=self.pk)).latest('timestamp')
            else:
                last_entity = ChatEntity.objects.latest('timestamp')
            if self.messages.latest('-timestamp').timestamp < last_entity.timestamp:
                raise ValidationError('At least one message has been included in previous entities')
