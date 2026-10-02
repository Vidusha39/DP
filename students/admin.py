from django.contrib import admin
from .models import Guardian, Student

class StudentInline(admin.TabularInline):
    model = Student
    extra = 0
    fields = ('admission_number', 'name_with_initials_sinhala', 'applied_grade', 'assigned_class', 'status')
    readonly_fields = ('admission_number', 'name_with_initials_sinhala', 'applied_grade')

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('full_name_sinhala', 'primary_phone', 'whatsapp_phone', 'linked_teacher', 'student_count')
    search_fields = ('full_name_sinhala', 'primary_phone', 'whatsapp_phone', 'address')
    inlines = [StudentInline]

    def student_count(self, obj):
        return obj.students.count()
    student_count.short_description = 'සිසුන් ගණන'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'name_with_initials_sinhala', 'applied_grade', 'assigned_class', 'status', 'guardian_phone')
    list_filter = ('status', 'applied_grade', 'assigned_class')
    search_fields = ('admission_number', 'full_name_sinhala', 'name_with_initials_sinhala', 'guardian__primary_phone')

    def guardian_phone(self, obj):
        return obj.guardian.primary_phone
    guardian_phone.short_description = 'භාරකරුගේ දුරකථනය'
