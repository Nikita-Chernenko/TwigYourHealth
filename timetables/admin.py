from django.contrib import admin

from timetables.models import TimeTable, Shift, Visit


@admin.register(TimeTable)
class TimetableAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    exclude = []

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    exclude = []
