from django.contrib import admin

from accounts.models import User, Doctor, Patient, Hospital, PrivateDoctor, PublicDoctor, Gender, AgeGap, DoctorSphere, \
    City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    pass


@admin.register(AgeGap)
class GapAgeAdmin(admin.ModelAdmin):
    pass


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    pass


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(PrivateDoctor)
class PrivateDoctorAdmin(admin.ModelAdmin):
    pass


@admin.register(PublicDoctor)
class PublicDoctorAdmin(admin.ModelAdmin):
    pass


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    pass


@admin.register(DoctorSphere)
class DoctorSphereAdmin(admin.ModelAdmin):
    pass
