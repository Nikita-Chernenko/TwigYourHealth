from django.contrib.auth.views import login, password_change
from django.urls import path

from accounts.forms import LoginViewForm
from accounts.views import patient_sign_up, public_doctor_sign_up, private_doctor_sign_up, logout, profile, update, \
    self_profile, relationships_update, review_create_update, review_delete, user_retrieve, _success_change_password

urlpatterns = [
    path('relationships/<int:pk>/update', relationships_update, name='relationships-update'),
    path('sign-up/patient-sign-up/', patient_sign_up, name='patient-sign-up'),
    path('sign-up/public-doctor-sign-up/', public_doctor_sign_up, name='public-doctor-sign-up'),
    path('sign-up/private-doctor-sign-up/', private_doctor_sign_up, name='private-doctor-sign-up'),
    path('logout/', logout, name='logout'),
    path('login/', login, {'template_name': 'accounts/login.html', 'authentication_form': LoginViewForm}, name='login'),
    path('profile/', self_profile, name='self-profile'),
    path('profile/<int:pk>', profile, name='profile'),
    path('profile/update/', update, name='update-profile'),
    path('review/create-update/<int:doctor_sphere_id>/', review_create_update, name='review-create'),
    path('review/create-update/<int:doctor_sphere_id>/<int:pk>/', review_create_update, name='review-update'),
    path('review/delete/', review_delete, name='review-delete'),
    path('profile/change-password/', password_change, {'template_name': 'accounts/change_password.html',
                                                       'post_change_redirect': 'success-change-password'},
         name='change-password'),
    path('user/<int:pk>/', user_retrieve, name='user-retrieve'),
    path('success-change-password', _success_change_password, name='success-change-password')
]
