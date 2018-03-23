from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout as _logout
from django.db.transaction import atomic
from django.forms import formset_factory
from django.shortcuts import redirect, get_object_or_404

from accounts.forms import UserPatientForm, PatientForm, UserDoctorForm, DoctorPublicDoctorForm, \
    PublicDoctorForm, DoctorPrivateDoctorForm, PrivateDoctorForm, UserForm
from accounts.models import User
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


def private_doctor_public_profile(request, user, request_user):
    pass


def public_doctor_public_profile(request, user, request_user):
    pass


@login_required
def profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    request_user = request.user
    self = request_user == user
    if self:
        if request_user.is_patient:
            return patient_profile(request, request_user)
        elif request_user.is_doctor and request_user.doctor.is_private:
            return private_doctor_profile(request, request_user)
        elif request_user.is_doctor:
            return public_doctor_profile(request, request_user)
    if request_user.is_patient:
        return patient_public_profile(request, user, request_user)
    elif request_user.is_doctor and request_user.doctor.is_private:
        return private_doctor_public_profile(request, user, request_user)
    elif request_user.is_doctor:
        return public_doctor_public_profile(request, user, request_user)


@render_to('accounts/patient_profile.html')
def patient_profile(request, user):
    patient = user.patient
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


@render_to('accounts/public_doctor_profile.html')
def public_doctor_profile(request):
    return {}


@render_to('accounts/private_doctor_profile.html')
def private_doctor_profile(request):
    return {}


def patient_public_profile(request, user, request_user):
    pass


def update(request):
    user = request.user
    if user.is_patient:
        return update_patient(request)
    elif user.is_doctor and user.doctor.is_private:
        return update_private_doctor(request)
    elif user.is_doctor:
        return update_public_doctor(request)


@render_to('accounts/patient_update.html')
def update_patient(request):
    patient = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user, prefix=user_prefix)
        patient_form = PatientForm(request.POST, instance=request.user.patient, prefix=patient_prefix)
        if user_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.user = user_form.save()
            patient.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=patient, prefix=user_prefix)
        patient_form = PatientForm(instance=patient.patient, prefix=patient_prefix)
    return {'user_form': user_form, 'patient_form': patient_form}


@render_to('accounts/public_doctor_update.html')
def update_public_doctor(request):
    doctor = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=doctor, prefix=user_prefix)
        doctor_form = DoctorPublicDoctorForm(request.POST, instance=doctor.doctor, prefix=doctor_prefix)
        public_doctor_form = PublicDoctorForm(request.POST, instance=doctor.doctor.publicdoctor,
                                              prefix=public_doctor_prefix)
        if user_form.is_valid() and doctor_form.is_valid() and public_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            public_doctor = public_doctor_form.save(commit=False)
            public_doctor.doctor = doctor
            public_doctor.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=doctor, prefix=user_prefix)
        doctor_form = DoctorPublicDoctorForm(instance=doctor.doctor, prefix=doctor_prefix)
        public_doctor_form = PublicDoctorForm(instance=doctor.doctor.publicdoctor,
                                              prefix=public_doctor_prefix)
    return {'user_form': user_form, 'doctor_form': doctor_form, 'public_doctor_form': public_doctor_form}


@render_to('accounts/private_doctor_update.html')
def update_private_doctor(request):
    doctor = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=doctor, prefix=user_prefix)
        doctor_form = DoctorPrivateDoctorForm(request.POST, instance=doctor.doctor, prefix=doctor_prefix)
        private_doctor_form = PrivateDoctorForm(request.POST, instance=doctor.doctor.privatedoctor,
                                                prefix=private_doctor_prefix)
        if user_form.is_valid() and doctor_form.is_valid() and private_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            private_doctor = private_doctor_form.save(commit=False)
            private_doctor.doctor = doctor
            private_doctor.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=doctor, prefix=user_prefix)
        doctor_form = DoctorPrivateDoctorForm(instance=doctor.doctor, prefix=doctor_prefix)
        private_doctor_form = PrivateDoctorForm(instance=doctor.doctor.privatedoctor,
                                                prefix=private_doctor_prefix)
    return {'user_form': user_form, 'doctor_form': doctor_form, 'private_doctor_form': private_doctor_form}
