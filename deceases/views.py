import json
import random
from itertools import groupby

from annoying.decorators import render_to
from django.db.models import Q, Sum, Count, Func, FloatField, ExpressionWrapper, F, IntegerField
from django.db.models.functions import Cast
from django.http import JsonResponse

from accounts.models import Doctor
from deceases.models import Symptom, Decease, BodyPart


@render_to('deceases/diagnostics.html')
def diagnostics(request):
    # body_symptoms = Symptom.objects.filter(~Q(body_part=None)) \
    #     .select_related('body_part', 'body_part__body_area').order_by('body_part__body_area', 'body_part')
    # body_symptoms = {
    #     key: {key: Symptom.objects.filter(pk__in=[s.id for s in symptoms]) for key, symptoms in
    #         groupby(symptoms, key=lambda s: s.body_part)} for
    #     key, symptoms in groupby(body_symptoms, key=lambda s: s.body_part.body_area)}
    # body_areas = BodyArea.objects.all().prefetch_related('bodypart_set', 'bodypart_set__symptom_set')
    body_symptoms = BodyPart.objects.\
        filter(pk__in=Symptom.objects.all().values_list('body_part',flat=True).distinct()).\
        prefetch_related('symptom_set')

    return {'body_symptoms': body_symptoms}


def symptoms_autocomplete(request):
    input_name = request.GET.get('name').lower()
    symptoms = list(Symptom.objects.filter(name__istartswith=input_name) \
                    .values('id', 'name').order_by('name'))
    if len(symptoms) < 10:
        symptoms += list(Symptom.objects.exclude(name__istartswith=input_name) \
                         .filter(aliases__icontains=input_name) \
                         .values('id', 'name').order_by('name'))[:(10 - len(symptoms))]
    return JsonResponse(data=symptoms, safe=False)


# WARNING tested only in sqlite
class Round(Func):
    function = 'ROUND'
    template = '%(function)s(%(expressions)s, 2)'


def deceases_by_symptoms(request):
    # TODO test it

    symptoms_ids = request.GET.getlist('symptoms[]')
    # symptoms_ids = [109, 32, 103]
    symptoms = Symptom.objects.filter(pk__in=symptoms_ids)
    whole_chance = Sum('deceasesymptom__chances')
    current_chance = Sum('deceasesymptom__chances', filter=Q(deceasesymptom__symptom__in=symptoms_ids))
    chance = Round(Cast(current_chance, FloatField()) / Cast(whole_chance, FloatField())) * 100
    deceases = list(Decease.objects.annotate(
        symptom_count=Count('deceasesymptom', filter=Q(deceasesymptom__symptom__in=symptoms_ids))) \
                    .filter(symptom_count__gte=2) \
                    .annotate(chance=chance).annotate(chance=ExpressionWrapper(
        F('chance') * F('symptom_count') / len(symptoms), output_field=IntegerField())).filter(
        ~Q(chance=None)).order_by('-chance')[:5].values('id', 'name', 'chance', 'sphere'))
    deceases_with_doctors = []
    for d in deceases:
        sphere = d.sphere
        doctors = list(Doctor.objects.filter(sphere=sphere).order_by('?')[:1000])
        doctors = list(sorted(doctors, key=lambda x: -x.rating))[:20]
        random.shuffle(doctors)
        doctors = doctors[:3]
        deceases_with_doctors.append({"decease": d, "doctors": doctors})

    data = json.dumps(deceases_with_doctors)

    return JsonResponse(data=data, safe=False)
