import json

from annoying.decorators import render_to
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import logout as _logout
from django.core.serializers import serialize
from django.db.transaction import atomic
from django.forms import formset_factory
from django.forms import model_to_dict
from django.http import Http404, HttpResponseForbidden, HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render_to_response
from django.views.decorators.http import require_http_methods

from accounts.forms import UserPatientForm, PatientForm, UserDoctorForm, DoctorPublicDoctorForm, \
    PublicDoctorForm, DoctorPrivateDoctorForm, PrivateDoctorForm, UserForm, ReviewForm
from accounts.models import Relationships, DoctorSphere, Review
from accounts.models import User
from deceases.forms import PatientDeceaseForm
from deceases.models import Decease

USER_PREFIX = 'user'
PATIENT_PREFIX = 'patient'
DOCTOR_PREFIX = 'doctor'
PUBLIC_DOCTOR_PREFIX = 'public_doctor'
PRIVATE_DOCTOR_PREFIX = 'private_doctor'


@render_to('accounts/patient/patient_sign_up.html')
@atomic
def patient_sign_up(request):
    user_form = UserPatientForm(request.POST or None, prefix=USER_PREFIX)
    patient_form = PatientForm(request.POST or None, prefix=PATIENT_PREFIX)
    if request.POST:
        if user_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.user = user_form.save()
            patient.save()
            login(request, patient.user)
            return redirect('self-profile')
    return {'user_form': user_form, 'patient_form': patient_form}


@render_to('accounts/doctor/public_doctor/public_doctor_sign_up.html')
@atomic
def public_doctor_sign_up(request):
    user_form = UserDoctorForm(request.POST or None, prefix=USER_PREFIX)
    doctor_form = DoctorPublicDoctorForm(request.POST or None, prefix=DOCTOR_PREFIX)
    public_doctor_form = PublicDoctorForm(request.POST or None, prefix=PUBLIC_DOCTOR_PREFIX)
    if request.POST:
        if user_form.is_valid() and doctor_form.is_valid() and public_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            public_doctor = public_doctor_form.save(commit=False)
            public_doctor.doctor = doctor
            public_doctor.save()
            login(request, doctor.user)
            return redirect('self-profile')
    return {'user_form': user_form, 'doctor_form': doctor_form, 'public_doctor_form': public_doctor_form}


@render_to('accounts/doctor/private_doctor/private_doctor_sign_up.html')
@atomic
def private_doctor_sign_up(request):
    user_form = UserDoctorForm(request.POST or None, prefix=USER_PREFIX)
    doctor_form = DoctorPrivateDoctorForm(request.POST or None, prefix=DOCTOR_PREFIX)
    private_doctor_form = PrivateDoctorForm(request.POST or None, prefix=PRIVATE_DOCTOR_PREFIX)
    if request.POST:
        if user_form.is_valid() and doctor_form.is_valid() and private_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            private_doctor = private_doctor_form.save(commit=False)
            private_doctor.doctor = doctor
            private_doctor.save()
            login(request, doctor.user)
            return redirect('self-profile')
    return {'user_form': user_form, 'doctor_form': doctor_form, 'private_doctor_form': private_doctor_form}


def logout(request):
    _logout(request)
    return redirect(request.META.get("HTTP_REFERER"))


def self_profile(request):
    return redirect('profile', request.user.id)


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
    if user.is_patient and request_user.is_doctor:
        return patient_public_profile(request, user, request_user)
    elif user.is_doctor and user.doctor.is_private and request_user.is_patient:
        return private_doctor_public_profile(request, user, request_user)
    elif user.is_doctor and request_user.is_patient:
        return public_doctor_public_profile(request, user, request_user)
    raise Http404('You are not allowed to view this page')


@render_to('accounts/patient/patient_profile.html')
def patient_profile(request, user):
    patient = user.patient
    medical_records = patient.patientdecease_set.all()
    PatientDeceaseFormSet = formset_factory(PatientDeceaseForm)
    if request.method == 'POST':
        patient_decease_formset = PatientDeceaseFormSet(request.POST)
        if patient_decease_formset.is_valid():
            for decease in patient_decease_formset:
                d = decease.save(commit=False)
                d.decease = Decease.objects.get(name=decease.cleaned_data['decease'])
                d.patient = patient
                d.save()
            patient_decease_formset = PatientDeceaseFormSet()
    else:
        patient_decease_formset = PatientDeceaseFormSet()
    return {'medical_records': medical_records, 'patient_decease_formset': patient_decease_formset}


def doctor_profile(request, user):
    doctor = user.doctor
    doctor_spheres = DoctorSphere.objects.filter(doctor=doctor).prefetch_related('review_set')
    return {'doctor': doctor, 'doctor_spheres': doctor_spheres}


@render_to('accounts/doctor/public_doctor/public_doctor_profile.html')
def public_doctor_profile(request, user):
    return doctor_profile(request, user)


@render_to('accounts/doctor/private_doctor/private_doctor_profile.html')
def private_doctor_profile(request, user):
    return doctor_profile(request, user)


@render_to('accounts/patient/patient_public_profile.html')
def patient_public_profile(request, user, request_user):
    patient = user.patient
    doctor = request_user.doctor
    relationships, _ = Relationships.objects.get_or_create(patient=patient, doctor=doctor)
    dict = {'patient': patient,
            'doctor': doctor, 'relationships': relationships}
    if relationships.patient_accept:
        medical_records = patient.patientdecease_set.all()
        for record in medical_records:
            record.form = PatientDeceaseForm(instance=record, initial={'decease': record.decease.name},
                                             auto_id=str(record.id) + '_%s')
        decease_form = PatientDeceaseForm(initial={'patient': patient.id})
        dict.update({'medical_records': medical_records, 'decease_form': decease_form})

    return dict


@render_to('accounts/doctor/doctor_public_profile.html')
def doctor_public_profile(request, user, request_user):
    doctor = user.doctor
    patient = request_user.patient
    relationships, _ = Relationships.objects.get_or_create(patient=patient, doctor=doctor)
    doctor_spheres = list(DoctorSphere.objects.filter(doctor=doctor).prefetch_related('review_set'))
    for sphere in doctor_spheres:
        if not Review.objects.filter(patient=patient, doctor_sphere=sphere).exists():
            sphere.form = ReviewForm()
    return {'doctor': doctor, 'patient': patient, 'doctor_spheres': doctor_spheres, 'relationships': relationships}


def private_doctor_public_profile(request, user, request_user):
    return doctor_public_profile(request, user, request_user)


def public_doctor_public_profile(request, user, request_user):
    return doctor_public_profile(request, user, request_user)


def update(request):
    user = request.user
    if user.is_patient:
        return update_patient(request)
    elif user.is_doctor and user.doctor.is_private:
        return update_private_doctor(request)
    elif user.is_doctor:
        return update_public_doctor(request)


@render_to('accounts/patient/patient_update.html')
@atomic
def update_patient(request):
    patient = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=request.user, prefix=USER_PREFIX)
        patient_form = PatientForm(request.POST, instance=request.user.patient, prefix=PATIENT_PREFIX)
        if user_form.is_valid() and patient_form.is_valid():
            patient = patient_form.save(commit=False)
            patient.user = user_form.save()
            patient.save()
            messages.add_message(request, messages.INFO, "Успешное обновление аккаунта")
            return redirect('self-profile')
    else:
        user_form = UserForm(instance=patient, prefix=USER_PREFIX)
        patient_form = PatientForm(instance=patient.patient, prefix=PATIENT_PREFIX)
    return {'user_form': user_form, 'patient_form': patient_form}


@render_to('accounts/doctor/public_doctor/public_doctor_update.html')
@atomic
def update_public_doctor(request):
    doctor = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=doctor, prefix=USER_PREFIX)
        doctor_form = DoctorPublicDoctorForm(request.POST, instance=doctor.doctor, prefix=DOCTOR_PREFIX)
        public_doctor_form = PublicDoctorForm(request.POST, instance=doctor.doctor.publicdoctor,
                                              prefix=PUBLIC_DOCTOR_PREFIX)
        if user_form.is_valid() and doctor_form.is_valid() and public_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            public_doctor = public_doctor_form.save(commit=False)
            public_doctor.doctor = doctor
            public_doctor.save()
            messages.add_message(request, messages.INFO, "Успешное обновление аккаунта")

            return redirect('self-profile')
    else:
        user_form = UserForm(instance=doctor, prefix=USER_PREFIX)
        doctor_form = DoctorPublicDoctorForm(instance=doctor.doctor, prefix=DOCTOR_PREFIX)
        public_doctor_form = PublicDoctorForm(instance=doctor.doctor.publicdoctor,
                                              prefix=PUBLIC_DOCTOR_PREFIX)
    return {'user_form': user_form, 'doctor_form': doctor_form, 'public_doctor_form': public_doctor_form}


@render_to('accounts/doctor/private_doctor/private_doctor_update.html')
@atomic
def update_private_doctor(request):
    doctor = request.user
    if request.method == 'POST':
        user_form = UserForm(request.POST, request.FILES, instance=doctor, prefix=USER_PREFIX)
        doctor_form = DoctorPrivateDoctorForm(request.POST, instance=doctor.doctor, prefix=DOCTOR_PREFIX)
        private_doctor_form = PrivateDoctorForm(request.POST, instance=doctor.doctor.privatedoctor,
                                                prefix=PRIVATE_DOCTOR_PREFIX)
        if user_form.is_valid() and doctor_form.is_valid() and private_doctor_form.is_valid():
            user = user_form.save()
            doctor = doctor_form.save(commit=False)
            doctor.user = user
            doctor.save()
            private_doctor = private_doctor_form.save(commit=False)
            private_doctor.doctor = doctor
            private_doctor.save()
            messages.add_message(request, messages.INFO, "Успешное обновление аккаунта")
            return redirect('self-profile')
    else:
        user_form = UserForm(instance=doctor, prefix=USER_PREFIX)
        doctor_form = DoctorPrivateDoctorForm(instance=doctor.doctor, prefix=DOCTOR_PREFIX)
        private_doctor_form = PrivateDoctorForm(instance=doctor.doctor.privatedoctor,
                                                prefix=PRIVATE_DOCTOR_PREFIX)
    return {'user_form': user_form, 'doctor_form': doctor_form, 'private_doctor_form': private_doctor_form}


@require_http_methods(["POST"])
def relationships_update(request, pk):
    patient = None
    doctor = None
    if request.user.is_patient:
        patient = request.user.patient
    elif request.user.is_doctor:
        doctor = request.user.doctor
    else:
        return JsonResponse(status=403, data='Only for doctors and patients')
    if doctor:
        relationships = get_object_or_404(Relationships, pk=pk, doctor=doctor)
        doctor_accept = request.POST.get('doctor_accept')
        if not doctor_accept:
            raise Http404('no doctor_accept param')
        doctor_accept = json.loads(doctor_accept)
        relationships.doctor_accept = doctor_accept
        relationships.patient_accept = True  # change in prod
    else:
        relationships = get_object_or_404(Relationships, pk=pk, patient=patient)
        patient_accept = request.POST.get('patient_accept')
        if not patient_accept:
            raise Http404('no patient_accept param')
        patient_accept = json.loads(patient_accept)
        relationships.patient_accept = patient_accept
    relationships.save()
    return JsonResponse(data=model_to_dict(relationships))


@require_http_methods(["POST"])
@user_passes_test(lambda user: user.is_patient)
def review_create_update(request, doctor_sphere_id, pk=None):
    doctor_sphere = get_object_or_404(DoctorSphere, pk=doctor_sphere_id)
    patient = request.user.patient
    if not Relationships.objects.filter(patient=patient, doctor=doctor_sphere.doctor).exists():
        return HttpResponseForbidden('No relation ship between the doctor and the user')
    instance = Review.objects.get(pk=pk) if pk else None
    review_form = ReviewForm(request.POST, instance=instance)
    if review_form.is_valid():
        review = review_form.save(commit=False)
        review.patient = request.user.patient
        review.doctor_sphere = doctor_sphere
        review.save()
        return HttpResponse('')
    return render_to_response('accounts/_review_create_update_form.html',
                              {'pk': pk, 'review_form': review_form, 'doctor_sphere_id': doctor_sphere_id})


@require_http_methods(["POST"])
@user_passes_test(lambda user: user.is_patient)
def review_delete(request):
    pk = request.POST.get('review_id')
    if not pk:
        raise Http404('no review_id')
    review = get_object_or_404(Review, pk=pk)
    if not review.patient == request.user.patient:
        return HttpResponseForbidden('The user is not the owner of the review')
    review.delete()
    return HttpResponse('')


# ------------------ API part

def user_retrieve(request, pk):
    user = get_object_or_404(User, pk=pk)
    user = serialize(queryset=[user], format='json')
    return JsonResponse(user, safe=False)


def _success_change_password(request):
    messages.add_message(request, messages.INFO, "Пароль успешно изменен")
    return redirect('self-profile')
