from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True)
    patronymic = models.CharField(max_length=64)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Hospital(models.Model):
    name = models.CharField('hospital name', max_length=256)
    address = models.CharField('hospital address', max_length=512)
    is_private = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skype = models.CharField('skype username', max_length=256, unique=True, null=True, blank=True)

    # TODO handle storing not as a row text
    skype_password = models.CharField('skype password', max_length=128, null=True, blank=True)

    is_private = models.BooleanField(default=True)
    accept_chat = models.BooleanField(default=True)
    accept_call = models.BooleanField(default=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, verbose_name='hospital', null=True, blank=True)
    personal_address = models.CharField("address if you don't work in clinic", max_length=512, null=True, blank=True)
    description = models.TextField('info about yourself')

    def __str__(self):
        return f'doctor {self.user}'


class DoctorSphere(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    sphere = models.ForeignKey('deceases.Sphere', on_delete=models.CASCADE)

    # calculated as gathering of all reviews
    rating = models.DecimalField('sphere rating', validators=[MinValueValidator(0), MaxValueValidator(100)],
                                 max_digits=5, decimal_places=2, default=0)


class PrivateDoctor(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    hour_rate = models.DecimalField('hour rate', max_digits=8, decimal_places=2)
    visit_price = models.DecimalField('visit price', max_digits=8, decimal_places=2)

    def __str__(self):
        return f'private {self.doctor} '


class PublicDoctor(models.Model):
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE)

    def __str__(self):
        return f'public {self.doctor}'


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField()
    deceases = models.ManyToManyField(to='deceases.Decease', through='deceases.PatientDecease')

    def __str__(self):
        return f'patient {self.user}'


class PatientDoctor(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.PROTECT)
    doctor = models.ForeignKey('Doctor', on_delete=models.PROTECT)

    class Meta:
        unique_together = [['patient', 'doctor']]

    def __str__(self):
        return f'relations {self.patient} {self.doctor}'
