from django.contrib import admin
from .models import Teacher, TeacherAllocation

class TeacherAllocationInline(admin.TabularInline):
    model = TeacherAllocation
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('title', 'name_with_initials', 'phone', 'whatsapp_phone', 'is_active')
    list_filter = ('is_active', 'title')
    search_fields = ('full_name_sinhala', 'name_with_initials', 'phone')
    inlines = [TeacherAllocationInline]

@admin.register(TeacherAllocation)
class TeacherAllocationAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'class_section', 'subject', 'is_class_teacher')
    list_filter = ('class_section__academic_year', 'class_section__grade_level', 'is_class_teacher')
