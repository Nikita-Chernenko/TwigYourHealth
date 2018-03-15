from django.urls import path

from deceases.views import symptoms_autocomplete, diagnostics, deceases_by_symptoms

urlpatterns = [
    path('symptoms-autocomplete/', symptoms_autocomplete, name='symptoms-autocomplete'),
    path('deceases-by-symptoms/', deceases_by_symptoms, name='deceases-by-symptoms'),
    path('diagnostics/', diagnostics, name='diagnostics')
]
