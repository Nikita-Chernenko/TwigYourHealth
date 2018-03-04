from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from users.models import User, Patient, PublicDoctor, Doctor, Hospital, PrivateDoctor


class UserSignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username','email', 'phone']


class UserPatientSignUpForm(UserSignUpForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
        return user


class PatientSignUpForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['birthday']


class UserDoctorSignUpForm(UserSignUpForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
        return user


class DoctorSignUpForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), widget=forms.CheckboxSelectMultiple,
                                      required=False)

    class Meta:
        model = Doctor
        fields = ['accept_call', 'accept_chat', 'hospital', 'personal_address', 'description']


class DoctorPublicDoctorSignUpForm(DoctorSignUpForm):
    def save(self, commit=True):
        doctor = super().save(commit=False)
        doctor.is_private = False
        if commit:
            doctor.save()
        return doctor


class DoctorPrivateDoctorSignUpForm(DoctorSignUpForm):
    def save(self, commit=True):
        doctor = super().save(commit=False)
        doctor.is_private = True
        if commit:
            doctor.save()
        return doctor


class PublicDoctorSignUpForm(forms.ModelForm):
    class Meta:
        model = PublicDoctor
        fields = []


class PrivateDoctorSignUpForm(forms.ModelForm):
    class Meta:
        model = PrivateDoctor
        fields = ['hour_rate', 'visit_price']
