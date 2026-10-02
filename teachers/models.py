from django.db import models
from django.contrib.auth.models import User
from academics.models import ClassSection

class Teacher(models.Model):
    TITLE_CHOICES = [
        ('VEN', 'පූජ්‍ය (Venerable)'),
        ('MR', 'ගුරු මයා (Mr.)'),
        ('MRS', 'ගුරු මිය (Mrs.)'),
        ('MISS', 'මෙනවිය (Miss)'),
    ]

    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='teacher_profile',
        verbose_name='පරිශීලක ගිණුම'
    )
    title = models.CharField(max_length=10, choices=TITLE_CHOICES, default='MR', verbose_name='ගෞරව නාමය')
    full_name_sinhala = models.CharField(max_length=255, verbose_name='සම්පූර්ණ නම (සිංහලෙන්)')
    name_with_initials = models.CharField(max_length=255, verbose_name='මුලකුරු සමඟ නම')
    phone = models.CharField(max_length=20, verbose_name='දුරකථන අංකය')
    whatsapp_phone = models.CharField(max_length=20, blank=True, verbose_name='වට්ස්ඇප් (WhatsApp) අංකය')
    address = models.TextField(blank=True, verbose_name='ලිපිනය')
    qualifications = models.TextField(blank=True, verbose_name='සුදුසුකම් (උදා: ධර්මාචාර්ය, උපාධිධාරී)')
    date_joined = models.DateField(null=True, blank=True, verbose_name='සේවයට බැඳුණු දිනය')
    is_active = models.BooleanField(default=True, verbose_name='ක්‍රියාකාරී ගුරුභවතෙක්ද?')

    class Meta:
        ordering = ['full_name_sinhala']
        verbose_name = 'ගුරුභවතා'
        verbose_name_plural = 'ගුරුභවතුන් (Teachers)'

    def __str__(self):
        title_str = self.get_title_display().split()[0]
        return f"{title_str} {self.name_with_initials}"

    @property
    def display_name(self):
        title_str = self.get_title_display().split()[0]
        return f"{title_str} {self.name_with_initials}"


class TeacherAllocation(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='allocations', verbose_name='ගුරුභවතා')
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE, related_name='teacher_allocations', verbose_name='පන්තිය')
    subject = models.CharField(max_length=100, default='බුද්ධ ධර්මය', verbose_name='විෂයය (Subject)')
    is_class_teacher = models.BooleanField(default=False, verbose_name='ප්‍රධාන පන්තිභාර ගුරුභවතාද?')

    class Meta:
        unique_together = ('teacher', 'class_section', 'subject')
        verbose_name = 'ගුරු අනුයුක්තය'
        verbose_name_plural = 'ගුරු අනුයුක්ත කිරීම් (Teacher Allocations)'

    def __str__(self):
        role_label = " (පන්තිභාර)" if self.is_class_teacher else ""
        return f"{self.teacher.display_name} -> {self.class_section} [{self.subject}]{role_label}"
