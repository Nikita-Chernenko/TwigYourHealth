from django.contrib import admin

from deceases.models import PatientDecease, Decease, Symptom, DeceaseSymptom


@admin.register(PatientDecease)
class PatientDeceaseAdmin(admin.ModelAdmin):
    fields = ['patient', 'decease', 'start_date', 'end_date', 'cured']


@admin.register(Decease)
class DeceaseAdmin(admin.ModelAdmin):
    fields = ['name', 'chronic', 'duration', 'contagiousness', 'malignancy', 'first_aid', 'occurrence']


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    fields = ['name', 'aliases']

@admin.register(DeceaseSymptom)
class DeceaseSymptomAdmin(admin.ModelAdmin):
    fields = ['symptom','decease','chances','occurrence']
