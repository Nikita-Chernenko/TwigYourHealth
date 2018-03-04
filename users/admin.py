from django.contrib import admin

from users.models import User, Doctor, Patient, Hospital


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ['username', 'password', 'first_name', 'patronymic', 'email', 'phone', 'is_doctor', 'is_patient']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    fields = ['user', 'hour_rate']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    fields = ['user', 'birthday']


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    fields = ['name', 'address']
