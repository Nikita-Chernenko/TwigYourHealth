import random

from annoying.decorators import render_to
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q, Sum, Count, Func, FloatField, ExpressionWrapper, F, IntegerField
from django.db.models.functions import Cast
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods

from accounts.models import Doctor, Relationships
from deceases.forms import PatientDeceaseForm
from deceases.models import Symptom, Decease, BodyPart, PatientDecease


@render_to('deceases/diagnostics.html')
def diagnostics(request):
    body_symptoms = BodyPart.objects.all()
    return {'body_symptoms': body_symptoms}


@render_to('deceases/_tree.html')
def symptom_tree(request):
    body_part_id = request.GET.get('body_part_id')
    symptoms = Symptom.objects.filter(body_part__pk=body_part_id)
    return {'tree': symptoms}


def symptoms_autocomplete(request):
    input_name = request.GET.get('name').lower()
    symptoms = list(Symptom.objects.filter(name__istartswith=input_name) \
                    .values('id', 'name').order_by('name'))
    if len(symptoms) < 10:
        symptoms += list(Symptom.objects.exclude(name__istartswith=input_name) \
                         .filter(aliases__icontains=input_name) \
                         .values('id', 'name').order_by('name'))[:(10 - len(symptoms))]
    return JsonResponse(data=symptoms, safe=False)


@require_http_methods(["POST"])
@user_passes_test(lambda user: user.is_doctor)
@render_to('deceases/_doctor_create_update_decease.html')
def doctor_create_update_decease(request):
    form = PatientDeceaseForm(request.POST)
    status_code = 409
    if form.is_valid():
        form = form.save(commit=False)
        if not Relationships.objects.filter(doctor=request.user.doctor, patient=form.patient).exists():
            return HttpResponseForbidden('No relation ship between doctor and user')
        form.author = request.user
        form.save()
        form = PatientDeceaseForm(initial={'patient': form.patient})
        status_code = 204 if hasattr(form, "id") else 201
    return {'add_decease_form': form, 'status_code': status_code}


@render_to('deceases/_medical_records.html')
def medical_records(request, patient_id):
    access = False
    if request.user.is_patient:
        access = request.user.patient.id == patient_id
    elif request.user.is_doctor:
        access = Relationships.objects.filter(doctor=request.user.doctor, patient__pk=patient_id).exists()
    if not access:
        return HttpResponseForbidden('You are neither the patient or no relationships between doctor and user')
    return {'medical_records': PatientDecease.objects.filter(patient__pk=patient_id)}


# WARNING tested only in sqlite
class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


@render_to('deceases/_deceases_with_doctors.html')
def deceases_by_symptoms(request):
    symptoms_ids = request.GET.getlist('symptoms[]')
    # symptoms_ids = [109, 32, 103]
    symptoms = Symptom.objects.filter(pk__in=symptoms_ids)
    whole_chance = Sum('deceasesymptom__chances')
    current_chance = Sum('deceasesymptom__chances', filter=Q(deceasesymptom__symptom__in=symptoms_ids))
    chance = Round(Cast(current_chance, FloatField()) / Cast(whole_chance, FloatField())) * 100
    deceases = list(Decease.objects.annotate(
        symptom_count=Count('deceasesymptom', filter=Q(deceasesymptom__symptom__in=symptoms_ids))) \
                    # .filter(symptom_count__gte=2) \
                    .annotate(chance=chance).annotate(chance=ExpressionWrapper(
        F('chance') * F('symptom_count') / len(symptoms), output_field=IntegerField())).filter(
        ~Q(chance=None)).order_by('-chance')[:5].values('id', 'name', 'chance', 'sphere'))
    deceases_with_doctors = []
    for d in deceases:
        sphere = d['sphere']
        doctors = list(Doctor.objects.filter(doctorsphere__sphere__pk=sphere).order_by('?')[:1000])
        doctors = list(sorted(doctors, key=lambda x: -x.rating))[:20]
        random.shuffle(doctors)
        doctors = doctors[:3]
        deceases_with_doctors.append({"decease": d, "doctors": doctors})

    return {'deceases_with_doctors': deceases_with_doctors}
