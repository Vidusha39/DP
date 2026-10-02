from django.db import models

class GradeLevel(models.Model):
    name = models.CharField(max_length=100, verbose_name='ශ්‍රේණියේ නම (Sinhala)')
    english_name = models.CharField(max_length=100, blank=True, verbose_name='නම (English)')
    order_index = models.PositiveIntegerField(default=1, verbose_name='අනුපිළිවෙල අංකය')
    description = models.TextField(blank=True, verbose_name='විස්තරය')

    class Meta:
        ordering = ['order_index']
        verbose_name = 'ශ්‍රේණිය'
        verbose_name_plural = 'ශ්‍රේණි (Grades)'

    def __str__(self):
        return self.name


class AcademicYear(models.Model):
    year = models.PositiveIntegerField(unique=True, verbose_name='අධ්‍යයන වර්ෂය')
    is_current = models.BooleanField(default=False, verbose_name='වත්මන් වර්ෂයද?')

    class Meta:
        ordering = ['-year']
        verbose_name = 'අධ්‍යයන වර්ෂය'
        verbose_name_plural = 'අධ්‍යයන වර්ෂ (Academic Years)'

    def __str__(self):
        return str(self.year)

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Classroom(models.Model):
    name = models.CharField(max_length=100, verbose_name='ශාලාව / කාමරයේ නම')
    capacity = models.PositiveIntegerField(default=40, verbose_name='ධාරිතාව')

    class Meta:
        verbose_name = 'පන්ති කාමරය / ශාලාව'
        verbose_name_plural = 'පන්ති කාමර / ශාලා'

    def __str__(self):
        return self.name


class ClassSection(models.Model):
    grade_level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name='sections', verbose_name='ශ්‍රේණිය')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='sections', verbose_name='අධ්‍යයන වර්ෂය')
    section_name = models.CharField(max_length=50, default='ප්‍රධාන', verbose_name='කාණ්ඩය / පන්තියේ නම')
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='පන්ති කාමරය')

    class Meta:
        unique_together = ('grade_level', 'academic_year', 'section_name')
        ordering = ['grade_level__order_index', 'section_name']
        verbose_name = 'පන්තිය'
        verbose_name_plural = 'පන්ති (Class Sections)'

    def __str__(self):
        if self.section_name and self.section_name != 'ප්‍රධාන':
            return f"{self.grade_level.name} - {self.section_name} ({self.academic_year.year})"
        return f"{self.grade_level.name} ({self.academic_year.year})"
