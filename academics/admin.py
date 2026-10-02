from django.contrib import admin
from .models import GradeLevel, AcademicYear, Classroom, ClassSection

@admin.register(GradeLevel)
class GradeLevelAdmin(admin.ModelAdmin):
    list_display = ('order_index', 'name', 'english_name')
    ordering = ('order_index',)

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ('year', 'is_current')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity')

@admin.register(ClassSection)
class ClassSectionAdmin(admin.ModelAdmin):
    list_display = ('grade_level', 'section_name', 'academic_year', 'classroom')
    list_filter = ('academic_year', 'grade_level')
