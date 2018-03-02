from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = PhoneNumberField(unique=True)
    patronymic = models.CharField(max_length=63)
    is_doctor = models.BooleanField(default=False)
    is_patient = models.BooleanField(default=False)


class Doctor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hour_rate = models.DecimalField(max_digits=8, decimal_places=2)


class Patient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    birthday = models.DateField()
