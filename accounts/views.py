from annoying.decorators import render_to
from django.contrib.auth.views import logout as _logout
from django.db.transaction import atomic
from django.forms import formset_factory
from django.shortcuts import redirect

from accounts.forms import UserPatientForm, PatientForm, UserDoctorForm, DoctorPublicDoctorForm, \
    PublicDoctorForm, DoctorPrivateDoctorForm, PrivateDoctorForm
from deceases.forms import PatientDeceaseForm

user_prefix = 'user'
patient_prefix = 'patient'
doctor_prefix = 'doctor'
public_doctor_prefix = 'public_doctor'
private_doctor_prefix = 'private_doctor'


@render_to('accounts/patient_sign_up.html')
@atomic
def patient_sign_up(request):
    user_form = UserPatientForm(request.POST or None, prefix=user_prefix)
    patient_form = PatientForm(request.POST or None, prefix=patient_prefix)
    if request.POST:
        if user_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.user = user_form.save()
            patient.save()
    return {'user_form': user_form, 'patient_form': patient_form}


@render_to('accounts/public_doctor_sign_up.html')
@atomic
def public_doctor_sign_up(request):
    user_form = UserDoctorForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPublicDoctorForm(request.POST or None, prefix=doctor_prefix)
    public_doctor_form = PublicDoctorForm(request.POST or None, prefix=public_doctor_prefix)
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


@render_to('accounts/private_doctor_sign_up.html')
@atomic
def private_doctor_sign_up(request):
    user_form = UserDoctorForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPrivateDoctorForm(request.POST or None, prefix=doctor_prefix)
    private_doctor_form = PrivateDoctorForm(request.POST or None, prefix=private_doctor_prefix)
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


def profile(request):
    user = request.user
    if user.is_patient:
        return patient_profile(request)
    elif user.is_doctor and user.doctor.is_public:
        return public_doctor_profile(request)
    elif user.is_doctor:
        return private_doctor_profile(request)


@render_to('accounts/patient_profile.html')
def patient_profile(request):
    patient = request.user.patient
    medical_records = patient.patientdecease_set.all()
    PatientDeceaseFormSet = formset_factory(PatientDeceaseForm)
    patient_decease_formset = PatientDeceaseFormSet(request.POST or None)
    if request.method == 'POST':
        if patient_decease_formset.is_valid():
            for decease in patient_decease_formset:
                decease = decease.save(commit=False)
                decease.patient = patient
                decease.save()
            patient_decease_formset = PatientDeceaseFormSet()
    return {'medical_records': medical_records, 'patient_decease_formset': patient_decease_formset}


def public_doctor_profile(request):
    pass


def private_doctor_profile(request):
    pass


def update(request):
    user = request.user
    if user.is_patient:
        return patient_update(request)
    elif user.is_doctor and user.doctor.is_public:
        return public_doctor_update(request)
    elif user.is_doctor:
        return private_doctor_update(request)


def patient_update(request):
    user_form = UserPatientForm(request.POST or None, prefix=user_prefix)
    patient_form = PatientForm(request.POST or None, prefix=patient_prefix)


def public_doctor_update(request):
    user_form = UserDoctorForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPrivateDoctorForm(request.POST or None, prefix=doctor_prefix)
    private_doctor_form = PrivateDoctorForm(request.POST or None, prefix=private_doctor_prefix)


def private_doctor_update(request):
    user_form = UserDoctorForm(request.POST or None, prefix=user_prefix)
    doctor_form = DoctorPrivateDoctorForm(request.POST or None, prefix=doctor_prefix)
    private_doctor_form = PrivateDoctorForm(request.POST or None, prefix=private_doctor_prefix)
