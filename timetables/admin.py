from django.contrib import admin

from timetables.models import ShiftType, Shift, Visit


@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    exclude = []


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    exclude = []
