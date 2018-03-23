from django.contrib.auth.views import login, password_change
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from accounts.forms import LoginViewForm
from accounts.views import patient_sign_up, public_doctor_sign_up, private_doctor_sign_up, logout, profile, update

urlpatterns = [
    path('sign-up/', TemplateView.as_view(template_name='accounts/sign_up.html'), name='sign-up'),
    path('sign-up/patient-sign-up/', patient_sign_up, name='patient-sign-up'),
    path('sign-up/public-doctor-sign-up/', public_doctor_sign_up, name='public-doctor-sign-up'),
    path('sign-up/private-doctor-sign-up/', private_doctor_sign_up, name='private-doctor-sign-up'),
    path('logout/', logout, name='logout'),
    path('login/', login, {'template_name': 'accounts/login.html', 'authentication_form': LoginViewForm}, name='login'),
    path('profile/<int:pk>', profile, name='profile'),
    path('profile/<int:pk>/change-password/', password_change, {'template_name': 'accounts/change_password.html',
                                                               'post_change_redirect': reverse_lazy('profile')},
         name='change-password'),
    path('profile/update/', update, name='update-profile')
]
