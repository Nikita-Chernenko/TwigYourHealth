from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from users.models import Doctor, Patient


class TimeTable(models.Model):
    doctor = models.ForeignKey(Doctor, verbose_name='doctor', on_delete=models.CASCADE)
    start = models.TimeField('start of the shift')
    end = models.TimeField('end of the shift')
    gap = models.DurationField('time of a visit', null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.gap = (self.gap // 60) * 60
        super(TimeTable, self).save(force_insert=False, force_update=False, using=None,
                                    update_fields=None)


class Shift(models.Model):
    timetable = models.ForeignKey(TimeTable, verbose_name='timetable', on_delete=models.CASCADE)
    day = models.DateField('day of the shift')


class Visit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    start = models.TimeField('start of the visit')
    end = models.TimeField('end of the visit')

    def __init__(self, *args, **kwargs):
        super(Visit, self).__init__(*args, **kwargs)
        self.__original_start = self.start
        self.__original_end = self.end

    def clean(self):
        start, end = self.start, self.end
        if start and end:
            start_changed, end_changed = self.__original_start != start, self.__original_end != end
            if start_changed or end_changed:

                # check that current gap is relevant to shift gap
                gap = self.shift and self.shift.timetable and self.shift.timetable.gap or False
                if gap and ((datetime.combine(date.today(), end) - datetime.combine(date.today(), start)) != gap):
                    minutes = gap.seconds // 60
                    raise ValidationError(f'Gap must be {minutes} minutes')

                # check if current time clashes with other visits
                if self.shift and self.start and self.end:
                    visits_this_day = Visit.objects.filter(shift__day=self.shift.day)
                    if start_changed and visits_this_day.filter(
                            (Q(start__lte=start) & Q(end__gte=start)) |
                            (Q(end__gte=end) & Q(start__lte=end)) |
                            (Q(start__gte=start) & Q(end__lte=end))).exists():
                        raise ValidationError(f'Visit for this time already exists')
