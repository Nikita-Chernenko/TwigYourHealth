from django.urls import path

from timetables.views import timetable

urlpatterns = [
    path('<int:doctor_pk>/', timetable, name='timetable'),
]
