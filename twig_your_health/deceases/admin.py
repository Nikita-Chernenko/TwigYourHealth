from django.contrib import admin

from deceases.models import PatientDecease, Decease, Symptom, DeceaseSymptom, BodyPart, PatientSymptomDecease


@admin.register(PatientDecease)
class PatientDeceaseAdmin(admin.ModelAdmin):
    pass

@admin.register(Decease)
class DeceaseAdmin(admin.ModelAdmin):
    pass

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    pass

@admin.register(DeceaseSymptom)
class DeceaseSymptomAdmin(admin.ModelAdmin):
    pass

@admin.register(BodyPart)
class BodyPartAdmin(admin.ModelAdmin):
    pass


@admin.register(PatientSymptomDecease)
class PatientSymptomDeceaseAdmin(admin.ModelAdmin):
    pass