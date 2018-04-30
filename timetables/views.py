from datetime import datetime, timedelta

from annoying.decorators import render_to
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from accounts.models import Doctor
from timetables.forms import ShiftForm, ShiftTypeForm, VisitForm
from timetables.models import Shift, Visit, ShiftType


# TODO check relationships/ divide for patient and doctor
@render_to('accounts/doctor/timetable.html')
def timetable(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    today = datetime.today()
    # TODO check that visits are related to the shifts
    shift_types = ShiftType.objects.filter(doctor=doctor).prefetch_related(
        Prefetch('shift_set', queryset=Shift.objects.filter(day__gte=today, day__lt=today + timedelta(days=14))),
        'shift_set__visit_set')
    return {'shift_types': shift_types, 'doctor': doctor}


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_doctor)
@render_to('accounts/doctor/_shift_form.html')
def shift_update_create(request, pk=None):
    instance = get_object_or_404(Shift, pk=pk) if pk else None
    doctor = request.user.doctor
    form = ShiftForm(request.POST or None, instance=instance, doctor=doctor)
    if form.is_valid():
        form.save()
        return HttpResponse('success')
    return {'shift_form': form, 'update': pk}


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_doctor)
@render_to('accounts/doctor/')
def shift_type_create(request, pk=None):
    request.POST._mutable = True
    request.POST['doctor'] = request.user.doctor
    instance = get_object_or_404(Shift, pk=pk) if pk else None
    form = ShiftTypeForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return HttpResponse('success')
    return {'shift_type_form': form, 'update': pk}


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_patient)
def visit_create(request, doctor_pk=None):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    patient = request.user.patient
    request.POST._mutable = True
    request.POST.update({'doctor': doctor, 'patient': patient})
    form = VisitForm(request.POST)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'errors': form.errors, 'success': False})


@require_http_methods(['POST'])
@user_passes_test(lambda u: u.is_patient)
def visit_remove(request, pk):
    visit = get_object_or_404(Visit, pk=pk)
    visit.delete()
    return JsonResponse({'success': True})
