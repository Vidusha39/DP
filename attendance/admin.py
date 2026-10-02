from django.contrib import admin
from .models import SundaySession, AttendanceRecord

@admin.register(SundaySession)
class SundaySessionAdmin(admin.ModelAdmin):
    list_display = ('date', 'academic_year', 'term', 'notes')
    list_filter = ('academic_year', 'term')

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'class_section', 'status', 'marked_by')
    list_filter = ('session__date', 'status', 'class_section')
    search_fields = ('student__full_name_sinhala', 'student__name_with_initials_sinhala')
