from decimal import Decimal
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Patient
from communication.models import CallEntity, ChatEntity
from timetables.models import Visit

interaction_limit = models.Q(app_label='communication', model='callentity') | \
                    models.Q(app_label='communication', model='chatentity') | \
                    models.Q(app_label='timetables', model='visit')


class Order(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, limit_choices_to=interaction_limit)
    object_id = models.PositiveIntegerField()
    interaction = GenericForeignKey('content_type', 'object_id')
    sum = models.PositiveIntegerField('sum to pay', blank=True)
    payed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    # AWARE this is a db loop but it's impossible to filter by it. Don't set it manually
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        unique_together = [['object_id', 'content_type']]

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        self.__original_content_type = getattr(self, 'content_type', None)
        self.__original_object_id = self.object_id

    def __str__(self):
        return f'{self.interaction} - {self.sum} - {self.payed}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # calculate sum of the interaction
        content_type_changed = self.__original_content_type != getattr(self, 'content_type', None)
        object_id_changed = self.__original_object_id != self.object_id
        if (content_type_changed or object_id_changed) and getattr(self, 'content_type', False) and self.object_id:
            model = self.content_type.model_class()
            model_id = self.object_id
            sum = None
            patient = None
            if model is Visit:
                visit = Visit.objects.get(pk=model_id)
                patient = visit.patient
                doctor = visit.shift.shift_type.doctor.privatedoctor
                sum = doctor.visit_price
            elif model is CallEntity:
                call_entity = CallEntity.objects.get(pk=model_id)
                patient = call_entity.patient
                doctor = call_entity.doctor.privatedoctor
                # TODO update with new logic
                hours = (call_entity.end - call_entity.start).seconds / 3600
                sum = doctor.hour_rate * hours
            elif model is ChatEntity:
                chat_entity = ChatEntity.objects.get(pk=model_id)
                patient = chat_entity.patient
                doctor = chat_entity.doctor.privatedoctor
                hours = chat_entity.hours
                sum = int(doctor.hour_rate * Decimal(hours))
            self.sum = sum
            self.patient = patient
        super(Order, self).save(force_insert, force_update, using, update_fields)

    def clean(self):
        # check that doctor is private
        if getattr(self, 'content_type', False) and self.object_id:
            content_type_changed = getattr(self, '__original_content_type', True) or \
                                   self.__original_content_type != self.content_type
            object_id_changed = getattr(self, '__original_object_id', True) or \
                                self.__original_object_id != self.object_id
            if (content_type_changed or object_id_changed) and \
                    getattr(self, 'content_type', False) and self.object_id:
                doctor = None
                model = self.content_type.model_class()
                model_id = self.object_id
                if model is Visit:
                    visit = Visit.objects.get(pk=model_id)
                    doctor = visit.shift.shift_type.doctor
                elif model is CallEntity:
                    call_entity = CallEntity.objects.get(pk=model_id)
                    doctor = call_entity.doctor
                elif model is ChatEntity:
                    chat_entity = ChatEntity.objects.get(pk=model_id)
                    doctor = chat_entity.doctor

                if not doctor.is_private:
                    raise ValidationError('This doctor is public')
