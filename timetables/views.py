from copy import deepcopy
from datetime import datetime, timedelta

from annoying.decorators import render_to
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_http_methods

from accounts.models import Doctor
from timetables.forms import ShiftForm, ShiftTypeForm, VisitForm
from timetables.models import Shift, Visit, ShiftType

# TODO check relationships/ divide for patient and doctor
from utils.checks import has_relationships

SHIFT_TYPE_PREFIX = 'shift_type'
SHIFT_PREFIX = 'shift'


@render_to('timetables/timetable.html')
def timetable(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    user = request.user
    shift_type_form = None
    shift_form = None
    if user.is_doctor:
        if not user.doctor.id == doctor_pk:
            return HttpResponseForbidden('You are not the doctor')
        shift_type_form = ShiftTypeForm(prefix=SHIFT_TYPE_PREFIX)
        shift_form = ShiftForm(prefix=SHIFT_PREFIX, doctor=doctor)
    elif user.is_patient:
        if not has_relationships(doctor_pk, user.patient.id):
            return HttpResponseForbidden('You are not connected with the doctor')
    else:
        return HttpResponseForbidden('You are not doctor or patient')
    today = datetime.today()
    # TODO check that visits are related to the shifts
    shift_types = ShiftType.objects.filter(doctor=doctor).prefetch_related(
        Prefetch('shift_set', queryset=Shift.objects.filter(day__gte=today, day__lt=today + timedelta(days=14))),
        'shift_set__visit_set')
    return {'shift_types': shift_types, 'doctor': doctor, 'shift_type_form': shift_type_form, 'shift_form': shift_form}


@user_passes_test(lambda u: u.is_doctor)
def self_timetable(request):
    return redirect('timetable', request.user.doctor.id)


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_doctor)
@render_to('timetables/_shift_form.html')
def shift_create_update(request, pk=None):
    instance = get_object_or_404(Shift, pk=pk) if pk else None
    doctor = request.user.doctor
    form = ShiftForm(request.POST, instance=instance, doctor=doctor, prefix=SHIFT_PREFIX)
    if form.is_valid():
        form.save()
        return HttpResponse('')
    return {'shift_form': form, 'update': True if pk else False}


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_doctor)
@render_to('timetables/_shift_type_form.html')
def shift_type_create_update(request, pk=None):
    data = deepcopy(request.POST)
    data[SHIFT_TYPE_PREFIX + '-doctor'] = request.user.doctor.id
    instance = get_object_or_404(Shift, pk=pk) if pk else None
    form = ShiftTypeForm(data, instance=instance, prefix=SHIFT_TYPE_PREFIX)
    if form.is_valid():
        form.save()
        return HttpResponse('')
    return {'shift_type_form': form, 'update': True if pk else False}


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_patient)
def visit_create(request):
    patient = request.user.patient
    data = deepcopy(request.POST)
    data['patient'] = patient.id
    form = VisitForm(data)
    if form.is_valid():
        visit = form.save()
        return JsonResponse({'success': True, 'visit_id': visit.id})
    return JsonResponse({'errors': form.errors, 'success': False})


@require_http_methods(['POST'])
def visit_remove(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    if request.user.is_patient:
        if visit.patient.id != request.user.patient.id:
            return HttpResponseForbidden("You are not the creator")
    elif request.user.is_doctor:
        if visit.shift.shift_type.doctor.id != request.user.doctor.id:
            return HttpResponseForbidden("This isn't your visit")
    else:
        return HttpResponseForbidden("You are not either doctor or patient")
    visit.delete()
    return JsonResponse({'success': True})
