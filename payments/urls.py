from django.urls import path
from payments.views import payment

urlpatterns = [
    path('payment_page/', payment, name='payment'),
]