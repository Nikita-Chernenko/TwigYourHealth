from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F
from django.utils.timezone import now

from users.models import Patient
from utils.validators import comma_separated_field


class Symptom(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    aliases = models.TextField(validators=[comma_separated_field], blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and not self.aliases:
            self.aliases = self.name
        super(Symptom, self).save(force_insert, force_update, using, update_fields)


class Decease(models.Model):
    name = models.CharField(max_length=256, db_index=True)
    chronic = models.BooleanField(default=False)
    symptoms = models.ManyToManyField(to=Symptom, through='DeceaseSymptom')
    duration = models.PositiveSmallIntegerField()
    contagiousness = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    malignancy = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    first_aid = models.TextField()
    occurrence = models.PositiveIntegerField(default=1)  # How many times this decease has occurred


class DeceaseSymptom(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    decease = models.ForeignKey(Decease, on_delete=models.CASCADE)

    # Will change periodically, calculated as division of the occurrence to the symptom occurrence
    # Not a property because it's crucial to use it in SQL queries,
    # May be not equal to the division, don't rely on it
    # Can't be managed in save because of complexity and
    # inconsistency of the occurrence and the symptom occurrence at the moment of the saving
    chances = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])

    occurrence = models.PositiveIntegerField(default=1)  # How many times this symptom has occurred for the decease

    class Meta:
        unique_together = [['symptom', 'decease']]



class PatientDecease(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    decease = models.ForeignKey(Decease, on_delete=models.PROTECT)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    cured = models.BooleanField(default=False)


class PatientSymptomDecease(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    decease = models.ForeignKey(Decease, on_delete=models.CASCADE, null=True, blank=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(PatientSymptomDecease, self).__init__(*args,**kwargs)
        self.__original_decease = self.decease

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.decease and self.symptom:
            # create new symptom of decease because it occurred and doesn't exist
            if not self.symptom in self.decease.symptoms.all():
                DeceaseSymptom.objects.create(decease=self.decease, symptom=self.symptom)
            # update the existing decease symptom
            else:
                DeceaseSymptom.objects.filter(decease=self.decease, symptom=self.symptom).update(
                    occurrence=F('occurrence') + 1)
            # decease has been either set or changed
            if not self.__original_decease == self.decease:
                # if decease has been changed, minus occurrence of the previous one
                if self.__original_decease:
                    self.__original_decease.occurrence = F('occurrence') - 1
                    self.__original_decease.save()
                # update occurrence of new decease
                DeceaseSymptom.objects.filter(decease=self.decease, symptom=self.symptom).update(
                    occurrence=F('occurrence') + 1)
