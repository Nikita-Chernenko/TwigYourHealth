from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from material import Layout, Row, Column

from accounts.models import User, Patient, PublicDoctor, Doctor, Hospital, PrivateDoctor


class LoginViewForm(AuthenticationForm):
    layout = Layout(Row('username', 'password'))


class UserForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'phone']

    layout = Layout(Row('username', 'email', 'phone'), Row('password1', 'password2'))


class UserPatientForm(UserForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
        return user


class PatientForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}),input_formats='%d-%m-%Y')

    class Meta:
        model = Patient
        fields = ['birthday']


class UserDoctorForm(UserForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
        return user


class DoctorForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all())

    class Meta:
        model = Doctor
        fields = ['accept_call', 'accept_chat', 'hospital', 'personal_address', 'description']

    layout = Layout(Row('accept_call', 'accept_chat'),Row('hospital'), Row('personal_address'), Row('description'))


class DoctorPublicDoctorForm(DoctorForm):
    def save(self, commit=True):
        doctor = super().save(commit=False)
        doctor.is_private = False
        if commit:
            doctor.save()
        return doctor


class DoctorPrivateDoctorForm(DoctorForm):
    def save(self, commit=True):
        doctor = super().save(commit=False)
        doctor.is_private = True
        if commit:
            doctor.save()
        return doctor


class PublicDoctorForm(forms.ModelForm):
    class Meta:
        model = PublicDoctor
        fields = []


class PrivateDoctorForm(forms.ModelForm):
    class Meta:
        model = PrivateDoctor
        fields = ['hour_rate', 'visit_price']
    layout = Layout(Row('hour_rate','visit_price'))
