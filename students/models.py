from django.db import models
from django.contrib.auth.models import User
from academics.models import GradeLevel, ClassSection
from teachers.models import Teacher
from datetime import date

class Guardian(models.Model):
    full_name_sinhala = models.CharField(max_length=255, verbose_name='දෙමාපිය / භාරකරුගේ නම')
    primary_phone = models.CharField(max_length=20, db_index=True, verbose_name='ප්‍රධාන දුරකථන අංකය')
    whatsapp_phone = models.CharField(max_length=20, blank=True, verbose_name='වට්ස්ඇප් (WhatsApp) අංකය')
    address = models.TextField(verbose_name='ලිපිනය')
    occupation = models.CharField(max_length=100, blank=True, verbose_name='රැකියාව')
    
    # Normalized relationship: If this guardian is a teacher in the Dhamma school
    linked_teacher = models.ForeignKey(
        Teacher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='guardian_profiles',
        verbose_name='දහම් පාසලේ ගුරුභවතෙක් නම් (Linked Teacher)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'දෙමාපිය / භාරකරු'
        verbose_name_plural = 'දෙමාපියන් / භාරකරුවන් (Guardians)'

    def __str__(self):
        if self.linked_teacher:
            return f"{self.full_name_sinhala} (ගුරු: {self.linked_teacher.display_name})"
        return f"{self.full_name_sinhala} ({self.primary_phone})"


class Student(models.Model):
    GENDER_CHOICES = [
        ('MALE', 'පිරිමි (Male)'),
        ('FEMALE', 'ගැහැණු (Female)'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'අනුමැතිය අපේක්ෂිත (Pending Verification)'),
        ('APPROVED', 'අනුමත කළ (Active Student)'),
        ('REJECTED', 'ප්‍රතික්ෂේපිත (Rejected)'),
        ('INACTIVE', 'අක්‍රිය (Inactive)'),
    ]

    RELATIONSHIP_CHOICES = [
        ('FATHER', 'පියා (Father)'),
        ('MOTHER', 'මව (Mother)'),
        ('GUARDIAN', 'භාරකරු (Guardian)'),
        ('OTHER', 'වෙනත් (Other)'),
    ]

    # Admission number is entered manually by the Teacher or Principal prior to approval
    admission_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        unique=True,
        verbose_name='ඇතුළත් වීමේ අංකය (Admission No)'
    )
    full_name_sinhala = models.CharField(max_length=255, verbose_name='සම්පූර්ණ නම (සිංහලෙන්)')
    name_with_initials_sinhala = models.CharField(max_length=255, verbose_name='මුලකුරු සමඟ නම')
    dob = models.DateField(verbose_name='උපන් දිනය')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='MALE', verbose_name='ස්ත්‍රී / පුරුෂ භාවය')
    
    # 1:N normalized guardian relationship
    guardian = models.ForeignKey(
        Guardian, 
        on_delete=models.CASCADE, 
        related_name='students', 
        verbose_name='දෙමාපිය / භාරකරු'
    )
    relationship_to_guardian = models.CharField(
        max_length=20, 
        choices=RELATIONSHIP_CHOICES, 
        default='FATHER', 
        verbose_name='භාරකරුගේ ඥාතිත්වය'
    )

    applied_grade = models.ForeignKey(
        GradeLevel, 
        on_delete=models.PROTECT, 
        related_name='applied_students', 
        verbose_name='ඉල්ලුම් කරන ශ්‍රේණිය'
    )
    assigned_class = models.ForeignKey(
        ClassSection, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='students', 
        verbose_name='අනුයුක්ත පන්තිය'
    )

    medical_notes = models.TextField(blank=True, verbose_name='සෞඛ්‍ය ගැටළු / ආසාත්මිකතා (ඇත්නම්)')
    special_notes = models.TextField(blank=True, verbose_name='වෙනත් විශේෂ සටහන්')

    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='PENDING', 
        verbose_name='ලියාපදිංචි තත්ත්වය'
    )
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='verified_students', 
        verbose_name='තහවුරු කළ පරිශීලකයා'
    )
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name='තහවුරු කළ දිනය')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ලියාපදිංචි වූ දිනය')

    class Meta:
        ordering = ['applied_grade__order_index', 'admission_number', 'name_with_initials_sinhala']
        verbose_name = 'ශිෂ්‍යයා'
        verbose_name_plural = 'සිසුන් (Students)'

    def __str__(self):
        adm = f"[{self.admission_number}] " if self.admission_number else "[නොලැබිණි] "
        return f"{adm}{self.name_with_initials_sinhala} - {self.applied_grade.name}"

    @property
    def age(self):
        if not self.dob:
            return None
        today = date.today()
        return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
