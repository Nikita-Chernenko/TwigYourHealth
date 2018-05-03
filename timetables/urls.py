from django.urls import path

from timetables.views import timetable, visit_create, visit_remove

urlpatterns = [
    path('<int:doctor_pk>/', timetable, name='timetable'),
    path('visit-create/', visit_create, name='visit-create'),
    path('visit-remove/<int:pk>/', visit_remove, name='visit-remove')
]
