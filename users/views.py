from annoying.decorators import render_to
from django.contrib.auth.views import logout as _logout
from django.db.transaction import atomic
from django.shortcuts import redirect

from users.forms import UserPatientSignUpForm, PatientSignUpForm, UserDoctorSignUpForm, DoctorPublicDoctorSignUpForm, \
    PublicDoctorSignUpForm, DoctorPrivateDoctorSignUpForm, PrivateDoctorSignUpForm


# TODO handle clinic creation

@render_to('users/patient_sign_up.html')
@atomic
def patient_sign_up(request):
    user_prefix = 'user'
    patient_prefix = 'patient'
    user_form = UserPatientSignUpForm(request.POST or None, prefix=user_prefix)
    patient_form = PatientSignUpForm(request.POST or None, prefix=patient_prefix)
    if request.POST:
        if user_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.user = user_form.save()
            patient.save()
    return {'user_form': user_form, 'patient_form': patient_form}


@render_to('users/public_doctor_sign_up.html')
@atomic
def public_doctor_sign_up(request):
    user_prefix = 'user'
    doctor_prefix = 'doctor'
    public_doctor_prefix = 'public_doctor'
    user_form = UserDoctorSignUpForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPublicDoctorSignUpForm(request.POST or None, prefix=doctor_prefix)
    public_doctor_form = PublicDoctorSignUpForm(request.POST or None, prefix=public_doctor_prefix)
    if request.POST:
        if user_form.is_valid() and doctor_form.is_valid() and public_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            public_doctor = public_doctor_form.save(commit=False)
            public_doctor.doctor = doctor
            public_doctor.save()
    return {'user_form': user_form, 'doctor_form': doctor_form, 'public_doctor_form': public_doctor_form}


@render_to('users/private_doctor_sign_up.html')
@atomic
def private_doctor_sign_up(request):
    user_prefix = 'user'
    doctor_prefix = 'doctor'
    private_doctor_prefix = 'private_doctor'
    user_form = UserDoctorSignUpForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPrivateDoctorSignUpForm(request.POST or None, prefix=doctor_prefix)
    private_doctor_form = PrivateDoctorSignUpForm(request.POST or None, prefix=private_doctor_prefix)
    if request.POST:
        if user_form.is_valid() and doctor_form.is_valid() and private_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            private_doctor = private_doctor_form.save(commit=False)
            private_doctor.doctor = doctor
            private_doctor.save()
    return {'user_form': user_form, 'doctor_form': doctor_form, 'private_doctor_form': private_doctor_form}


def logout(request):
    _logout(request)
    return redirect(request.META.get("HTTP_REFERER"))
