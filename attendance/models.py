from django.db import models
from django.contrib.auth.models import User
from academics.models import AcademicYear, ClassSection
from students.models import Student

class SundaySession(models.Model):
    TERM_CHOICES = [
        (1, '1 වන වාරය (Term 1)'),
        (2, '2 වන වාරය (Term 2)'),
        (3, '3 වන වාරය (Term 3)'),
    ]

    date = models.DateField(unique=True, verbose_name='දිනය (Sunday Date)')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sunday_sessions', verbose_name='අධ්‍යයන වර්ෂය')
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES, default=1, verbose_name='වාරය')
    notes = models.CharField(max_length=255, blank=True, verbose_name='විශේෂ සටහන (උදා: පෝය දින වැඩසටහන)')

    class Meta:
        ordering = ['-date']
        verbose_name = 'දහම් පාසල් දිනය'
        verbose_name_plural = 'දහම් පාසල් දින (Sunday Sessions)'

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} ({self.get_term_display()})"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'පැමිණි (Present)'),
        ('ABSENT', 'නොපැමිණි (Absent)'),
        ('EXCUSED', 'නිවාඩු (Excused)'),
        ('LATE', 'ප්‍රමාද (Late)'),
    ]

    session = models.ForeignKey(SundaySession, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='දිනය')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='ශිෂ්‍යයා')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='attendance_records', verbose_name='පන්තිය')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PRESENT', verbose_name='පැමිණීමේ තත්ත්වය')
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='සටහන් කළ පරිශීලකයා')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='යාවත්කාලීන වූ දිනය')

    class Meta:
        unique_together = ('session', 'student')
        verbose_name = 'පැමිණීමේ සටහන'
        verbose_name_plural = 'පැමිණීමේ සටහන් (Attendance Records)'

    def __str__(self):
        return f"{self.student.name_with_initials_sinhala} - {self.session.date} ({self.get_status_display()})"
