from django import forms
from .models import GradeLevel, Classroom, ClassSection, AcademicYear

class GradeLevelForm(forms.ModelForm):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.all().order_by('name'),
        required=False,
        empty_label='-- ස්ථානයක් / ශාලාවක් වෙන් කර නැත --',
        label='ස්ථානය / පන්ති කාමරය (Allocated Location)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = GradeLevel
        fields = ['name', 'english_name', 'order_index', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'උදා: 1 ශ්‍රේණිය, ධර්මාචාර්ය, පෙර පාසල',
                'required': True,
            }),
            'english_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Grade 1, Dharmacharya',
            }),
            'order_index': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'උදා: 1',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ශ්‍රේණිය පිළිබඳ කෙටි විස්තරයක් (අවශ්‍ය නම් පමණි)',
            }),
        }
        labels = {
            'name': 'ශ්‍රේණියේ නම (Sinhala)',
            'english_name': 'ඉංග්‍රීසි නම (English)',
            'order_index': 'අනුපිළිවෙල අංකය (Order Index)',
            'description': 'විස්තරය (Description)',
        }

    def __init__(self, *args, current_section=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_section and current_section.classroom:
            self.fields['classroom'].initial = current_section.classroom


class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'උදා: ප්‍රධාන ධර්ම ශාලාව / 1 වන ගොඩනැගිල්ල - කාමර අංක 03',
                'required': True,
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'උදා: 40',
                'required': True,
            }),
        }
        labels = {
            'name': 'ශාලාව හෝ ස්ථානයේ නම (Location / Hall Name)',
            'capacity': 'උපරිම ධාරිතාව (Capacity)',
        }


class GradeLocationAllocationForm(forms.Form):
    grade_level = forms.ModelChoiceField(
        queryset=GradeLevel.objects.all().order_by('order_index'),
        label='ශ්‍රේණිය (Grade)',
        widget=forms.Select(attrs={'class': 'form-select', 'required': True})
    )
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.all().order_by('name'),
        required=False,
        empty_label='-- ස්ථානයක් වෙන් කර නැත (Unassigned) --',
        label='අනුයුක්ත කරන ස්ථානය / ශාලාව (Assigned Location)',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
