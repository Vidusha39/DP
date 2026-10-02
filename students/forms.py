from django import forms
from .models import Student, Guardian
from academics.models import GradeLevel
from teachers.models import Teacher
from datetime import date

class StudentRegistrationForm(forms.Form):
    # Student Details
    full_name_sinhala = forms.CharField(
        label='ශිෂ්‍යයාගේ සම්පූර්ණ නම (සිංහලෙන්)',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: කහඳවිටගේ අනුහස් තිසර පෙරේරා',
            'required': True
        })
    )
    name_with_initials_sinhala = forms.CharField(
        label='මුලකුරු සමඟ නම',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: කේ. ඒ. තිසර පෙරේරා',
            'required': True
        })
    )
    dob = forms.DateField(
        label='උපන් දිනය (Date of Birth)',
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'class': 'form-control',
            'required': True
        })
    )
    gender = forms.ChoiceField(
        label='ස්ත්‍රී / පුරුෂ භාවය',
        choices=Student.GENDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    applied_grade = forms.ModelChoiceField(
        label='ඇතුළත් වීමට බලාපොරොත්තු වන ශ්‍රේණිය',
        queryset=GradeLevel.objects.all().order_by('order_index'),
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    medical_notes = forms.CharField(
        label='සෞඛ්‍ය ගැටළු / ආසාත්මිකතා (ඇත්නම් පමණක් ලියන්න)',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'කිසිවක් නැත්නම් හිස්ව තබන්න'
        })
    )
    special_notes = forms.CharField(
        label='වෙනත් විශේෂ සටහන්',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'විශේෂ දක්ෂතා හෝ සටහන්'
        })
    )

    # Guardian Details
    guardian_name = forms.CharField(
        label='දෙමාපිය / භාරකරුගේ සම්පූර්ණ නම',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: කහඳවිටගේ සුනිල් පෙරේරා',
            'required': True
        })
    )
    relationship_to_guardian = forms.ChoiceField(
        label='ශිෂ්‍යයාට ඇති ඥාතිත්වය',
        choices=Student.RELATIONSHIP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    guardian_phone = forms.CharField(
        label='ප්‍රධාන දුරකථන අංකය (ඇමතුම් සඳහා)',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: 0771234567',
            'type': 'tel',
            'required': True
        })
    )
    guardian_whatsapp = forms.CharField(
        label='වට්ස්ඇප් (WhatsApp) අංකය',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: 0771234567 (පණිවිඩ එවීමට)',
            'type': 'tel'
        })
    )
    guardian_address = forms.CharField(
        label='ස්ථිර ලිපිනය',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'නිවසේ ලිපිනය',
            'required': True
        })
    )
    guardian_occupation = forms.CharField(
        label='රැකියාව',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'උදා: රජයේ සේවක / ව්‍යාපාරික'
        })
    )

    # Teacher child option
    is_teacher_child = forms.BooleanField(
        label='මම / භාරකරු මෙම දහම් පාසලේ ගුරුභවතෙකි (Teacher)',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'isTeacherCheckbox'})
    )
    linked_teacher = forms.ModelChoiceField(
        label='ගුරුභවතා තෝරන්න',
        queryset=Teacher.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'teacherSelect'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applied_grade'].queryset = GradeLevel.objects.all().order_by('order_index')

    def save(self):
        cd = self.cleaned_data
        phone = cd['guardian_phone'].strip()

        # 1. Normalize Guardian: Check if guardian with this primary phone already exists (1-to-Many support)
        linked_tch = cd['linked_teacher'] if cd.get('is_teacher_child') else None

        guardian, created = Guardian.objects.get_or_create(
            primary_phone=phone,
            defaults={
                'full_name_sinhala': cd['guardian_name'].strip(),
                'whatsapp_phone': (cd['guardian_whatsapp'] or phone).strip(),
                'address': cd['guardian_address'].strip(),
                'occupation': cd.get('guardian_occupation', '').strip(),
                'linked_teacher': linked_tch,
            }
        )

        if not created:
            # If existed, update fields if newly provided
            if linked_tch and not guardian.linked_teacher:
                guardian.linked_teacher = linked_tch
                guardian.save()

        # 2. Create Student with PENDING status (requires verification before officially enrolled)
        student = Student.objects.create(
            full_name_sinhala=cd['full_name_sinhala'].strip(),
            name_with_initials_sinhala=cd['name_with_initials_sinhala'].strip(),
            dob=cd['dob'],
            gender=cd['gender'],
            guardian=guardian,
            relationship_to_guardian=cd['relationship_to_guardian'],
            applied_grade=cd['applied_grade'],
            medical_notes=cd.get('medical_notes', '').strip(),
            special_notes=cd.get('special_notes', '').strip(),
            status='PENDING',
        )

        return student
