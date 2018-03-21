from django.urls import path

from deceases.views import symptoms_autocomplete, diagnostics, deceases_by_symptoms, symptom_tree

urlpatterns = [
    path('symptoms-autocomplete/', symptoms_autocomplete, name='symptoms-autocomplete'),
    path('deceases-by-symptoms/', deceases_by_symptoms, name='deceases-by-symptoms'),
    path('symptom_tree/', symptom_tree, name='symptom-tree'),
    path('diagnostics/', diagnostics, name='diagnostics')
]
