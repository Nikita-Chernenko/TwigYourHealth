from django.contrib import admin

from payments.models import Order, Payment


@admin.register(Order)
class NotificationAdmin(admin.ModelAdmin):
    exclude = []

admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    exclude = []