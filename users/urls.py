from django.contrib.auth.views import login
from django.urls import path
from django.views.generic import TemplateView

from users.views import patient_sign_up, public_doctor_sign_up, private_doctor_sign_up, logout

urlpatterns = [
    path('sign-up/', TemplateView.as_view(template_name='users/sign_up.html')),
    path('patient-sign-up/', patient_sign_up, name='patient-sign-up'),
    path('public-doctor-sign-up/', public_doctor_sign_up, name='public-doctor-sign-up'),
    path('private-doctor-sign-up/', private_doctor_sign_up, name='private-doctor-sign-up'),
    path('logout/', logout, name='logout'),
    path('login/', login, {'template_name': 'users/login.html'}, name='login'),
]
