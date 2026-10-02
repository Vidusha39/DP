from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('ADMIN', 'පද්ධති පරිපාලක (System Admin)'),
        ('PRINCIPAL', 'ප්‍රධානාචාර්ය (Principal)'),
        ('TEACHER', 'ගුරුභවතා (Teacher)'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='TEACHER', verbose_name='භූමිකාව (Role)')
    phone = models.CharField(max_length=20, blank=True, verbose_name='දුරකථන අංකය')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'පරිශීලක පැතිකඩ'
        verbose_name_plural = 'පරිශීලක පැතිකඩවල්'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.user.is_superuser

    @property
    def is_principal(self):
        return self.role == 'PRINCIPAL'

    @property
    def is_teacher(self):
        return self.role == 'TEACHER'
