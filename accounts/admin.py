from django.contrib import admin

from accounts.models import User, Doctor, Patient, Hospital, PrivateDoctor, PublicDoctor


# TODO change fields

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(PrivateDoctor)
class PrivateDoctorAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(PublicDoctor)
class PublicDoctorAdmin(admin.ModelAdmin):
    exclude = []
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    exclude = []
