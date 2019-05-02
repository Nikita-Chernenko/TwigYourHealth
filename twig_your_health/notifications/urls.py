from django.urls import path

from notifications.views import mark_read

urlpatterns = [
    path('mark-read', mark_read, name='mark-read')
]
