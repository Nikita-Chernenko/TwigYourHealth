from django.contrib import admin

from payments.models import Order


@admin.register(Order)
class NotificationAdmin(admin.ModelAdmin):
    exclude = []

