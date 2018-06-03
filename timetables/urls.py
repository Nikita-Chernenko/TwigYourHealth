from django.urls import path

from timetables.views import timetable, visit_create, visit_remove, self_timetable, shift_type_create_update, \
    shift_create_update

urlpatterns = [
    path('', self_timetable, name='self-timetable'),
    path('<int:doctor_pk>/', timetable, name='timetable'),
    path('visit-create/', visit_create, name='visit-create'),
    path('visit-remove/<int:pk>/', visit_remove, name='visit-remove'),
    path('shift-type-create/', shift_type_create_update, name='shift-type-create'),
    path('shift-type-create/<int:pk>/', shift_type_create_update, name='shift-type-update'),
    path('shift-create/', shift_create_update, name='shift-create'),
    path('shift-create/<int:pk>/', shift_create_update, name='shift-update'),
]
