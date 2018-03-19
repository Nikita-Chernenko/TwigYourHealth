from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F
from django.utils.timezone import now

from accounts.models import Patient
from utils.validators import comma_separated_field


class BodyArea(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class BodyPart(models.Model):
    body_area = models.ForeignKey(BodyArea, on_delete=models.PROTECT)
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return f'{self.body_area} - {self.name}'


class Symptom(models.Model):
    body_part = models.ForeignKey(BodyPart, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=512, db_index=True, unique=True)
    aliases = models.TextField(validators=[comma_separated_field], blank=True, null=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and not self.aliases:
            self.aliases = self.name
        super(Symptom, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name


class Sphere(models.Model):
    name = models.CharField('name', max_length=256, unique=True)


class Decease(models.Model):
    sphere = models.ForeignKey(Sphere, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, db_index=True, unique=True)
    chronic = models.BooleanField(default=False)
    symptoms = models.ManyToManyField(to=Symptom, through='DeceaseSymptom')
    duration = models.PositiveSmallIntegerField(default=10)
    contagiousness = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    malignancy = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)])
    description = models.TextField()
    diagnostics = models.TextField(blank=True, null=True)
    treatment = models.TextField(blank=True, null=True)
    passing = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    occurrence = models.PositiveIntegerField(default=1)  # How many times this decease has occurred

    def __str__(self):
        return self.name


class DeceaseSymptom(models.Model):
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    decease = models.ForeignKey(Decease, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['symptom', 'decease']]

    # Will change periodically, calculated as division of the occurrence to the symptom occurrence
    # Not a property because it's crucial to use it in SQL queries,
    # May be not equal to the division, don't rely on it
    # Can't be managed in save because of complexity and
    # inconsistency of the occurrence and the symptom occurrence at the moment of the saving
    chances = models.PositiveSmallIntegerField(validators=[MaxValueValidator(100)], default=50)

    occurrence = models.PositiveIntegerField(default=1)  # How many times this symptom has occurred for the decease

    def __str__(self):
        return f'{self.symptom} - {self.decease}'


class PatientDecease(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    decease = models.ForeignKey(Decease, on_delete=models.PROTECT)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    cured = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.patient} {self.decease}'


class PatientSymptomDecease(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    decease = models.ForeignKey(Decease, on_delete=models.CASCADE, null=True, blank=True)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(PatientSymptomDecease, self).__init__(*args, **kwargs)
        self.__original_decease = self.decease

    def __str__(self):
        return f'{self.patient} - {self.decease} - {self.symptom}'

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
