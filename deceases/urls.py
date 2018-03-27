from django.urls import path

from deceases.views import symptoms_autocomplete, diagnostics, deceases_by_symptoms, symptom_tree, \
    doctor_create_update_decease, medical_records

urlpatterns = [
    path('symptoms-autocomplete/', symptoms_autocomplete, name='symptoms-autocomplete'),
    path('deceases-by-symptoms/', deceases_by_symptoms, name='deceases-by-symptoms'),
    path('doctor-create-update-decease/', doctor_create_update_decease, name='doctor-create-update-decease'),
    path('doctor-create-update-decease/<int:patient_decease_id>/', doctor_create_update_decease, name='doctor-create-update-decease'),
    path('medical-records/<int:patient_id>', medical_records, name='medical-records'),
    path('symptom_tree/', symptom_tree, name='symptom-tree'),
    path('diagnostics/', diagnostics, name='diagnostics')
]
