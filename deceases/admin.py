from django.contrib import admin

from deceases.models import PatientDecease, Decease, Symptom, DeceaseSymptom, BodyPart, BodyArea, PatientSymptomDecease


@admin.register(PatientDecease)
class PatientDeceaseAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Decease)
class DeceaseAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(DeceaseSymptom)
class DeceaseSymptomAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(BodyArea)
class BodyAreaAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(PatientSymptomDecease)
class PatientSymptomDeceaseAdmin(admin.ModelAdmin):
    exclude = []