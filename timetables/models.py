from datetime import date, datetime, timedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Doctor, Patient, Relationships


class ShiftType(models.Model):
    title = models.CharField('name of the shift', max_length=255)
    doctor = models.ForeignKey(Doctor, verbose_name='doctor', on_delete=models.CASCADE)
    start = models.TimeField('start of the shift')
    end = models.TimeField('end of the shift')
    gap = models.DurationField('time of a visit', null=True, blank=True, help_text='time in minutes')

    class Meta:
        unique_together = [['doctor', 'start', 'end']]

    def __init__(self, *args, **kwargs):
        super(ShiftType, self).__init__(*args, **kwargs)
        self.__original_gap = self.gap

    def __str__(self):
        return f'{self.title}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.__original_gap and self.gap:
            self.gap = self.gap * 60
        elif not self.gap:
            self.gap = timedelta(minutes=15)
        super(ShiftType, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)

    @property
    def visit_gaps(self):
        start = datetime.combine(date.today(), self.start)
        gaps = []
        while (start + self.gap).time() < self.end:
            gaps.append([start, start + self.gap])
            start += self.gap
        return gaps


class Shift(models.Model):
    shift_type = models.ForeignKey(ShiftType, verbose_name='shift_type', on_delete=models.CASCADE)
    day = models.DateField('day of the shift')

    class Meta:
        ordering = ['day']
        unique_together = [['shift_type', 'day']]

    def __str__(self):
        return f'{self.shift_type} - {self.day}'

    @property
    def timetable_visits(self):
        gaps = self.shift_type.visit_gaps
        visits = list(self.visit_set.all())
        t_visits = []
        visit_ind = 0
        for gap in gaps:
            visit_time = \
                [datetime.combine(date.today(), visits[visit_ind].start),
                 datetime.combine(date.today(), visits[visit_ind].end)] \
                    if visit_ind < len(visits) \
                    else []
            if gap == visit_time:
                t_visits.append(visits[visit_ind])
                visit_ind += 1
            else:
                t_visits.append(gap)
        return t_visits


class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start = models.TimeField('start of the visit')
    end = models.TimeField('end of the visit')
    orders = GenericRelation('payments.Order', on_delete=models.CASCADE)

    class Meta:
        ordering = ['shift', 'start']
        unique_together = ['start', 'end', 'shift']

    def __init__(self, *args, **kwargs):
        super(Visit, self).__init__(*args, **kwargs)
        self.__original_start = self.start
        self.__original_end = self.end

    def __str__(self):
        return f'{self.start}-{self.end} {self.patient} - {self.shift}'

    def save(self, *args, **kwargs):
        if not self.pk:
            super(Visit, self).save(*args, **kwargs)
            from payments.models import Order
            order = Order(interaction=self)
            order.save()
        else:
            super(Visit, self).save(*args, **kwargs)

    def clean(self):
        start, end = self.start, self.end
        if start and end:
            start_changed, end_changed = self.__original_start != start, self.__original_end != end
            if start_changed or end_changed:
                visit_gap = [datetime.combine(date.today(), start), datetime.combine(date.today(), end)]
                if hasattr(self, 'shift') and hasattr(self.shift, 'shift_type') \
                        and not visit_gap in self.shift.shift_type.visit_gaps:
                    raise ValidationError('Wrong start/end')

                # check if current time clashes with other visits
                if hasattr(self, 'shift'):
                    visits_this_day = Visit.objects.filter(shift__day=self.shift.day)
                    if start_changed and visits_this_day.filter(start__exact=start).exists():
                        raise ValidationError(f'Visit for this time already exists')

        if hasattr(self, 'shift') and hasattr(self.shift, 'shift_type') \
                and hasattr(self.shift.shift_type, 'doctor') and hasattr(self, 'patient') \
                and not Relationships.objects.filter(patient=self.patient,
                                                     doctor=self.shift.shift_type.doctor).exists():
            raise ValidationError('the patient has no connection with doctor from the shift')

        if hasattr(self, 'shift') and self.shift.visit_set.filter(patient=self.patient):
            raise ValidationError("Patient can't create more than one visit per day")
