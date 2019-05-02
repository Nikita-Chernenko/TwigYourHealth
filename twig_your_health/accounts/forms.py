from datetime import datetime, timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm as _UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from material import Layout, Row

from accounts.models import User, Patient, PublicDoctor, Doctor, Hospital, PrivateDoctor, Review, City, DoctorSphere
from deceases.models import Sphere


class LoginViewForm(AuthenticationForm):
    username = forms.CharField(help_text='* ваш логин, email, телефон')
    layout = Layout(Row('username'), Row('password'))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'patronymic', 'username', 'email', 'phone', 'avatar']

    # layout = Layout(Row('username', 'email', 'phone', 'avatar'))


class UserCreationForm(_UserCreationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta(_UserCreationForm.Meta):
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone']

    # layout = Layout(Row('username', 'email', 'phone'), Row('password1', 'password2'))


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
        fields = ['birthday', 'gender', 'skype']

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if datetime.combine(date=birthday, time=datetime.now().time()) + timedelta(
                days=365 * 12) >= datetime.now():
            raise ValidationError('Вы слышком молоды, только 12+')
        return birthday


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

    # layout = Layout(Row('accept_call', 'accept_chat'), Row('hospital'), Row('personal_address'), Row('description'))


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

    # layout = Layout(Row('hour_rate', 'visit_price'))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'mark']

    layout = Layout(Row('comment'), Row('mark'))


class DoctorSearchForm(forms.Form):
    min_price = forms.IntegerField(required=False)
    max_price = forms.IntegerField(required=False)
    name = forms.CharField(required=False)
    surname = forms.CharField(required=False)
    sphere = forms.ModelChoiceField(queryset=Sphere.objects.all(), required=False)
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)
    TO_HIGH_PRICE, TO_LOW_PRICE = '1', '2'

    ordering = forms.ChoiceField(
        choices=(('0', '-------'), (TO_HIGH_PRICE, 'To high price'), (TO_LOW_PRICE, 'To low price')),
        required=False)
    only_public = forms.BooleanField(required=False)
    only_private = forms.BooleanField(required=False)
    layout = Layout(
        Row('name', 'surname', 'min_price', 'max_price'),
        Row('sphere', 'city', 'ordering', 'only_public', 'only_private')
    )

    def _get_qs(self):
        queryset = Doctor.objects.all()
        min_price = self.cleaned_data['min_price']
        max_price = self.cleaned_data['max_price']
        name = self.cleaned_data['name']
        surname = self.cleaned_data['surname']
        sphere = self.cleaned_data['sphere']
        city = self.cleaned_data['city']
        ordering = self.cleaned_data['ordering']
        only_private = self.cleaned_data['only_private']
        only_public = self.cleaned_data['only_public']
        if min_price:
            queryset = queryset.filter(privatedoctor__hour_rate__gte=min_price)
        if max_price:
            queryset = queryset.filter(privatedoctor__hour_rate__lte=max_price)
        if name:
            queryset = queryset.filter(user__first_name__icontains=name)
        if surname:
            queryset = queryset.filter(user__surname__icontais=surname)
        if sphere:
            queryset = queryset.filter(doctorsphere__sphere=sphere)
        if city:
            queryset = queryset.filter(user__city=city)
        if ordering:
            if ordering == self.TO_HIGH_PRICE:
                queryset = queryset.order_by('privatedoctor__hour_rate')
            elif ordering == self.TO_LOW_PRICE:
                queryset = queryset.order_by('-privatedoctor__hour_rate')
        if only_private:
            queryset = queryset.filter(privatedoctor__isnull=False)
        if only_public:
            queryset = queryset.filter(publicdoctor__isnull=False)
        return queryset


class DoctorSphereForm(forms.ModelForm):
    doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), widget=forms.HiddenInput())

    class Meta:
        model = DoctorSphere
        fields = ['doctor', 'sphere']
