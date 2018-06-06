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
    sum = models.PositiveIntegerField('sum to pay')
    payed = models.BooleanField(default=False)

    class Meta:
        unique_together = [['object_id', 'content_type']]

    def __init__(self, *args, **kwargs):
        super(Order, self).__init__(*args, **kwargs)
        if getattr(self, 'content_type', False) and self.object_id:
            self.__original_content_type = self.content_type
            self.__original_object_id = self.object_id

    def __str__(self):
        return f'{self.interaction} - {self.sum} - {self.payed}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # calculate sum of the interaction
        content_type_changed = getattr(self, '__original_content_type', False) and \
                               self.__original_content_type != self.content_type
        object_id_changed = getattr(self, '__original_object_id', False) and \
                            self.__original_object_id != self.object_id
        if content_type_changed or object_id_changed:
            model = self.content_type.model_class()
            model_id = self.object_id
            sum = None
            if isinstance(model, Visit):
                visit = Visit.objects.get(pk=model_id)
                doctor = visit.shift.timetable.doctor.privatedoctor
                sum = doctor.visit_price
            elif isinstance(model, CallEntity):
                call_entity = CallEntity.objects.get(pk=model_id)
                doctor = call_entity.doctor.privatedoctor
                hours = (call_entity.end - call_entity.start).seconds // 3600
                sum = doctor.hour_rate * hours
            elif isinstance(model, ChatEntity):
                chat_entity = ChatEntity.objects.get(pk=model_id)
                doctor = chat_entity.doctor.privatedoctor
                hours = chat_entity.hours
                sum = int(doctor.hour_rate * hours)
            self.sum = sum
        super(Order, self).save(force_insert, force_update, using, update_fields)

    def clean(self):
        # check that doctor is private
        if getattr(self, 'content_type', False) and self.object_id:
            content_type_changed = getattr(self, '__original_content_type', False) and \
                                   self.__original_content_type != self.content_type
            object_id_changed = getattr(self, '__original_object_id', False) and \
                                self.__original_object_id != self.object_id
            if content_type_changed or object_id_changed:
                doctor = None
                model = self.content_type.model_class()
                model_id = self.object_id
                if isinstance(model, Visit):
                    visit = Visit.objects.get(pk=model_id)
                    doctor = visit.shift.timetable.doctor
                elif isinstance(model, CallEntity):
                    call_entity = CallEntity.objects.get(pk=model_id)
                    doctor = call_entity.doctor
                elif isinstance(model, CallEntity):
                    call_entity = CallEntity.objects.get(pk=model_id)
                    doctor = call_entity.doctor

                if not doctor.is_private:
                    raise ValidationError('This doctor is public')


class Payment(models.Model):
    # AWARE this is a db loop but it's impossible to filter by it. Don't set it manually
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, blank=True)

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.patient} {self.order} {self.date}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        order = getattr(self, 'order', False) and self.order
        if not self.pk and order and getattr(order, 'content_type', False) and order.object_id:
            model = order.content_type.model_class()
            model_id = order.object_id
            patient = None
            if model is Visit:
                visit = Visit.objects.get(pk=model_id)
                patient = visit.patient
            elif model is CallEntity:
                call_entity = CallEntity.objects.get(pk=model_id)
                patient = call_entity.patient
            elif model is ChatEntity:
                chat_entity = ChatEntity.objects.get(pk=model_id)
                patient = chat_entity.patient
            self.patient = patient
            order.payed = True
            order.save()
        super(Payment, self).save(force_insert, force_update, using, update_fields)
