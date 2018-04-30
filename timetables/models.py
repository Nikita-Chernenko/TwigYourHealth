from datetime import date, datetime, timedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Doctor, Patient


class ShiftType(models.Model):
    title = models.CharField('name of the shift', max_length=255)
    doctor = models.ForeignKey(Doctor, verbose_name='doctor', on_delete=models.CASCADE)
    start = models.TimeField('start of the shift')
    end = models.TimeField('end of the shift')
    gap = models.DurationField('time of a visit', null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super(ShiftType, self).__init__(*args, **kwargs)
        self.__original_gap = self.gap

    def __str__(self):
        return f'{self.title}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.__original_gap and self.gap:
            self.gap = (self.gap // 60) * 60
        elif not self.gap:
            self.gap = timedelta(minutes=15)
        super(ShiftType, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)

    @property
    def visit_gaps(self):
        start = datetime.combine(date.today(), self.start)
        gaps = []
        while (start + self.gap).time()  < self.end:
            gaps.append([start, start + self.gap])
            start += self.gap
        return gaps


class Shift(models.Model):
    shift_type = models.ForeignKey(ShiftType, verbose_name='shift_type', on_delete=models.CASCADE)
    day = models.DateField('day of the shift')

    class Meta:
        ordering = ['day']

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
                t_visits.append(None)
        return t_visits


class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start = models.TimeField('start of the visit')
    end = models.TimeField('end of the visit')
    orders = GenericRelation('payments.Order', on_delete=models.CASCADE)

    class Meta:
        ordering = ['shift', 'start']

    def __init__(self, *args, **kwargs):
        super(Visit, self).__init__(*args, **kwargs)
        self.__original_start = self.start
        self.__original_end = self.end

    def __str__(self):
        return f'{self.start}-{self.end} {self.patient} - {self.shift}'

    def clean(self):
        start, end = self.start, self.end
        if start and end:
            start_changed, end_changed = self.__original_start != start, self.__original_end != end
            if start_changed or end_changed:
                visit_gap = [datetime.combine(date.today(), start), datetime.combine(date.today(), end)]
                if hasattr(self, 'shift') and hasattr(self.shift, 'shift_type') \
                        and not visit_gap in self.shift.shift_type.visit_gaps:
                    raise ValidationError('Wrong start/end')
                # # check that start and end in right shift boundaries
                # if hasattr(self, 'shift') and hasattr(self.shift, 'shift_type') and (
                #         self.shift.shift_type.end < end or self.shift.shift_type.start > start):
                #     raise ValidationError("start or end is not in the boundaries of the shift")
                #
                # # check that current gap is relevant to shift gap
                # gap = hasattr(self, 'shift') and hasattr(self.shift,
                #                                          'shift_type') and self.shift.shift_type.gap or False
                # if gap and ((datetime.combine(date.today(), end) - datetime.combine(date.today(), start)) != gap):
                #     minutes = gap.seconds // 60
                #     raise ValidationError(f'Gap must be {minutes} minutes')

                # check if current time clashes with other visits
                if hasattr(self, 'shift'):
                    visits_this_day = Visit.objects.filter(shift__day=self.shift.day)
                    if start_changed and visits_this_day.filter(start__exact=start).exists():
                        raise ValidationError(f'Visit for this time already exists')
