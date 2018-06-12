from django.urls import path
from payments.views import *

urlpatterns = [
    path('payment_page/<int:pk>/', payment, name='payment'),
    path('orders/<int:pk>/', orders, name='orders'),
]