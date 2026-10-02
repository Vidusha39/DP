from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from teachers.models import Teacher, TeacherAllocation
from academics.models import GradeLevel, AcademicYear, ClassSection

class TeacherManagementTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Principal User
        self.principal_user = User.objects.create_user(username='principal_test', password='password123')
        UserProfile.objects.create(user=self.principal_user, role='PRINCIPAL', phone='0711111111')

        # Create Regular Teacher User
        self.teacher_user = User.objects.create_user(username='teacher_test', password='password123')
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER', phone='0722222222')
        self.sample_teacher = Teacher.objects.create(
            user=self.teacher_user,
            title='MR',
            full_name_sinhala='ටෙස්ට් ගුරුභවතා',
            name_with_initials='ටී. ගුරුභවතා',
            phone='0722222222',
            is_active=True
        )

    def test_principal_can_access_teacher_list(self):
        self.client.login(username='principal_test', password='password123')
        response = self.client.get(reverse('teacher_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ටෙස්ට් ගුරුභවතා')

    def test_regular_teacher_cannot_access_teacher_list(self):
        self.client.login(username='teacher_test', password='password123')
        response = self.client.get(reverse('teacher_list'))
        # Should redirect to dashboard with access denied
        self.assertEqual(response.status_code, 302)

    def test_principal_can_create_teacher(self):
        self.client.login(username='principal_test', password='password123')
        post_data = {
            'username': 'new_teacher_1',
            'password': 'teacher123',
            'title': 'MRS',
            'full_name': 'නව ගුරු මහත්මිය',
            'name_initials': 'එන්. ගුරු',
            'phone': '0773333333',
            'whatsapp': '0773333333',
            'address': 'නො. 10, පාර',
            'qualifications': 'ධර්මාචාර්ය',
        }
        response = self.client.post(reverse('create_teacher'), post_data)
        self.assertRedirects(response, reverse('teacher_list'))

        # Verify created in DB
        self.assertTrue(Teacher.objects.filter(name_with_initials='එන්. ගුරු').exists())
        self.assertTrue(User.objects.filter(username='new_teacher_1').exists())

    def test_principal_can_edit_teacher(self):
        self.client.login(username='principal_test', password='password123')
        post_data = {
            'username': 'teacher_test_updated',
            'new_password': 'newpassword123',
            'title': 'VEN',
            'full_name': 'ටෙස්ට් ගුරුභවතා යාවත්කාලීන',
            'name_initials': 'ටී. ගුරුභවතා සංස්කරණය',
            'phone': '0799999999',
            'whatsapp': '0799999999',
            'address': 'නො. 20, විහාරය',
            'qualifications': 'රාජකීය පණ්ඩිත',
            'is_active': 'on',
        }
        response = self.client.post(reverse('edit_teacher', args=[self.sample_teacher.id]), post_data)
        self.assertRedirects(response, reverse('teacher_list'))

        self.sample_teacher.refresh_from_db()
        self.assertEqual(self.sample_teacher.title, 'VEN')
        self.assertEqual(self.sample_teacher.phone, '0799999999')
        self.assertEqual(self.sample_teacher.user.username, 'teacher_test_updated')
        # Check new password works
        login_success = self.client.login(username='teacher_test_updated', password='newpassword123')
        self.assertTrue(login_success)

    def test_principal_can_deactivate_and_delete_teacher(self):
        self.client.login(username='principal_test', password='password123')
        
        # Test deactivation via delete confirmation
        response = self.client.post(reverse('delete_teacher', args=[self.sample_teacher.id]), {'action': 'deactivate'})
        self.assertRedirects(response, reverse('teacher_list'))
        self.sample_teacher.refresh_from_db()
        self.assertFalse(self.sample_teacher.is_active)

        # Test toggle status
        response = self.client.get(reverse('toggle_teacher_status', args=[self.sample_teacher.id]))
        self.assertRedirects(response, reverse('teacher_list'))
        self.sample_teacher.refresh_from_db()
        self.assertTrue(self.sample_teacher.is_active)

        # Test permanent deletion
        response = self.client.post(reverse('delete_teacher', args=[self.sample_teacher.id]), {'action': 'delete'})
        self.assertRedirects(response, reverse('teacher_list'))
        self.assertFalse(Teacher.objects.filter(id=self.sample_teacher.id).exists())
        self.assertFalse(User.objects.filter(username='teacher_test').exists())
