from math import ceil

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F
from django.utils.timezone import now
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from accounts.models import Patient, User, Relationships, Gender, AgeGap
from utils.validators import comma_separated_field


class BodyPart(MPTTModel):
    name = models.CharField(max_length=256, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            on_delete=models.CASCADE)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class Symptom(MPTTModel):
    body_part = models.ForeignKey(BodyPart, on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=512, db_index=True, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True,
                            on_delete=models.CASCADE)
    aliases = models.TextField(validators=[comma_separated_field], blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk and not self.aliases:
            self.aliases = self.name
        super(Symptom, self).save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return f"{self.name} {self.body_part}"


class Sphere(models.Model):
    name = models.CharField('name', max_length=256, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


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

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DeceaseAgeGapGender(models.Model):
    decease = models.ForeignKey(Decease, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    age_gap = models.ForeignKey(AgeGap, on_delete=models.CASCADE)
    number = models.PositiveIntegerField('number of people in average to get decease from 10^6')


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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # handled in save for now for simplicity
        if hasattr(self, 'decease') and self.occurrence:
            self.chances = ceil(self.occurrence / self.decease.occurrence * 100)
        super(DeceaseSymptom, self).save(force_insert, force_update, using, update_fields)


class PatientDecease(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    decease = models.ForeignKey(Decease, on_delete=models.PROTECT)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)
    cured = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.PROTECT, blank=True)

    def __str__(self):
        return f'{self.patient} {self.decease}'

    def update_occurence(self):
        if not self.pk and hasattr(self, 'decease') and self.symptoms.exists():
            Decease.objects.filter(pk=self.decease.id).update(occurrence=F('occurrence') + 1)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not hasattr(self, "author") and hasattr(self, "patient"):
            self.author = self.patient.user
        self.update_occurence()
        super(PatientDecease, self).save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        if self.symptoms.exists():
            Decease.objects.filter(pk=self.decease.id).update(occurrence=F('occurrence') - 1)
        super(PatientDecease, self).delete(using, keep_parents)

    def clean(self):
        if hasattr(self, "author") and hasattr(self, "patient") and hasattr(self.author,
                                                                            'patient') and self.author.patient != self.patient:
            if not Relationships.objects.filter(patient=self.patient, doctor=self.author.doctor).exists():
                raise ValidationError(f'{self.author} is not able to add medical records for{self.patient}'
                                      f'request the access from the patient')
        super(PatientDecease, self).clean()


class PatientSymptomDecease(models.Model):
    patient_decease = models.ForeignKey(PatientDecease, on_delete=models.PROTECT, related_name='symptoms')
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super(PatientSymptomDecease, self).__init__(*args, **kwargs)
        self.__original_decease = hasattr(self, "patient_decease") and self.patient_decease.decease

    def __str__(self):
        return f'{self.patient_decease} - {self.symptom}'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if hasattr(self, 'patient_decease') and hasattr(self, 'symptom'):
            # TODO recheck the algo
            # create new symptom of decease because it occurred and doesn't exist
            decease = self.patient_decease.decease
            if self.symptom not in decease.symptoms.all():
                DeceaseSymptom.objects.create(decease=decease, symptom=self.symptom)
            # update the existing decease symptom
            else:
                DeceaseSymptom.objects.filter(decease=decease, symptom=self.symptom).update(
                    occurrence=F('occurrence') + 1)
            # decease has been either set or changed
            if not self.__original_decease == decease:
                # if decease has been changed, minus occurrence of the previous one
                if self.__original_decease:
                    self.__original_decease.occurrence = F('occurrence') - 1
                    self.__original_decease.save()
                # update occurrence of new decease
                DeceaseSymptom.objects.filter(decease=decease, symptom=self.symptom).update(
                    occurrence=F('occurrence') + 1)
        super(PatientSymptomDecease, self).save(force_insert, force_update, using, update_fields)
        # Update occurence of the decease
        if hasattr(self, 'patient_decease'):
            self.patient_decease.update_occurence()
