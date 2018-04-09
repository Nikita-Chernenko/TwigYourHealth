from django import forms
from django.contrib.auth.forms import UserCreationForm as _UserCreationForm, AuthenticationForm
from material import Layout, Row

from accounts.models import User, Patient, PublicDoctor, Doctor, Hospital, PrivateDoctor, Review


class LoginViewForm(AuthenticationForm):
    username = forms.CharField(help_text='username or email or phone')
    layout = Layout(Row('username', 'password'))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'avatar']

    layout = Layout(Row('username', 'email', 'phone', 'avatar'))


class UserCreationForm(_UserCreationForm):
    class Meta(_UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'phone']

    layout = Layout(Row('username', 'email', 'phone'), Row('password1', 'password2'))


class UserPatientForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_patient = True
        if commit:
            user.save()
        return user


class PatientForm(forms.ModelForm):
    birthday = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}))

    class Meta:
        model = Patient
        fields = ['birthday', 'gender']


class UserDoctorForm(UserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_doctor = True
        if commit:
            user.save()
        return user


class DoctorForm(forms.ModelForm):
    hospital = forms.ModelChoiceField(queryset=Hospital.objects.all(), required=False)

    class Meta:
        model = Doctor
        fields = ['accept_call', 'accept_chat', 'hospital', 'personal_address', 'description']

    layout = Layout(Row('accept_call', 'accept_chat'), Row('hospital'), Row('personal_address'), Row('description'))


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

    layout = Layout(Row('hour_rate', 'visit_price'))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'mark']
