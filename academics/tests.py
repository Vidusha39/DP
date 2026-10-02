from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

from accounts.models import UserProfile
from academics.models import GradeLevel, AcademicYear, Classroom, ClassSection
from students.models import Guardian, Student


class GradeAndLocationManagementTests(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Academic Year
        self.academic_year = AcademicYear.objects.create(year=2026, is_current=True)

        # 2. Users: Admin, Principal, Teacher
        self.admin_user = User.objects.create_user(username='admin_test', password='password123')
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')

        self.principal_user = User.objects.create_user(username='principal_test', password='password123')
        UserProfile.objects.create(user=self.principal_user, role='PRINCIPAL')

        self.teacher_user = User.objects.create_user(username='teacher_test', password='password123')
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER')

        # 3. Classrooms
        self.hall1 = Classroom.objects.create(name='ප්‍රධාන ධර්ම ශාලාව', capacity=60)
        self.hall2 = Classroom.objects.create(name='ශාලා අංක 02', capacity=40)

        # 4. Existing Grade
        self.grade1 = GradeLevel.objects.create(order_index=1, name='1 ශ්‍රේණිය', english_name='Grade 1')
        self.section1 = ClassSection.objects.create(
            grade_level=self.grade1,
            academic_year=self.academic_year,
            section_name='ප්‍රධාන',
            classroom=self.hall1
        )

    # --- Access Control Tests ---
    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse('grade_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

        response = self.client.get(reverse('grade_create'))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse('allocate_grade_location'))
        self.assertEqual(response.status_code, 302)

    def test_teacher_denied_access(self):
        self.client.login(username='teacher_test', password='password123')

        # Grade list
        response = self.client.get(reverse('grade_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

        # Grade create
        response = self.client.get(reverse('grade_create'))
        self.assertEqual(response.status_code, 302)

        # Grade edit
        response = self.client.get(reverse('grade_edit', args=[self.grade1.id]))
        self.assertEqual(response.status_code, 302)

        # Grade delete
        response = self.client.get(reverse('grade_delete', args=[self.grade1.id]))
        self.assertEqual(response.status_code, 302)

        # Allocate location
        response = self.client.get(reverse('allocate_grade_location'))
        self.assertEqual(response.status_code, 302)

    # --- Admin and Principal Grade Management Tests ---
    def test_admin_can_view_grade_list(self):
        self.client.login(username='admin_test', password='password123')
        response = self.client.get(reverse('grade_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1 ශ්‍රේණිය')
        self.assertContains(response, 'ප්‍රධාන ධර්ම ශාලාව')

    def test_principal_can_view_grade_list(self):
        self.client.login(username='principal_test', password='password123')
        response = self.client.get(reverse('grade_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1 ශ්‍රේණිය')

    def test_admin_can_create_grade_and_allocate_location(self):
        self.client.login(username='admin_test', password='password123')
        data = {
            'name': '2 ශ්‍රේණිය',
            'english_name': 'Grade 2',
            'order_index': 2,
            'description': 'දෙවන ශ්‍රේණිය',
            'classroom': self.hall2.id,
        }
        response = self.client.post(reverse('grade_create'), data)
        self.assertEqual(response.status_code, 302)

        # Verify GradeLevel was created
        grade2 = GradeLevel.objects.filter(name='2 ශ්‍රේණිය').first()
        self.assertIsNotNone(grade2)
        self.assertEqual(grade2.english_name, 'Grade 2')
        self.assertEqual(grade2.order_index, 2)

        # Verify ClassSection for 2026 was created with hall2
        section = ClassSection.objects.filter(grade_level=grade2, academic_year=self.academic_year).first()
        self.assertIsNotNone(section)
        self.assertEqual(section.classroom, self.hall2)

    def test_principal_can_edit_grade_and_location(self):
        self.client.login(username='principal_test', password='password123')
        data = {
            'name': '1 ශ්‍රේණිය (නව)',
            'english_name': 'Grade 1 New',
            'order_index': 1,
            'description': 'යාවත්කාලීන කළ විස්තරය',
            'classroom': self.hall2.id,
        }
        response = self.client.post(reverse('grade_edit', args=[self.grade1.id]), data)
        self.assertEqual(response.status_code, 302)

        self.grade1.refresh_from_db()
        self.assertEqual(self.grade1.name, '1 ශ්‍රේණිය (නව)')

        self.section1.refresh_from_db()
        self.assertEqual(self.section1.classroom, self.hall2)

    def test_admin_can_delete_grade_without_students(self):
        self.client.login(username='admin_test', password='password123')
        grade_to_delete = GradeLevel.objects.create(order_index=99, name='තාවකාලික ශ්‍රේණිය')

        # GET confirm delete page
        response = self.client.get(reverse('grade_delete', args=[grade_to_delete.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'තාවකාලික ශ්‍රේණිය')
        self.assertContains(response, 'මෙම ශ්‍රේණිය මකා දමන්න')

        # POST delete
        response = self.client.post(reverse('grade_delete', args=[grade_to_delete.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(GradeLevel.objects.filter(id=grade_to_delete.id).exists())

    def test_cannot_delete_grade_with_students(self):
        self.client.login(username='admin_test', password='password123')

        # Create a guardian & student attached to grade1
        guardian = Guardian.objects.create(full_name_sinhala='නිමල් පෙරේරා', primary_phone='0771122334')
        student = Student.objects.create(
            full_name_sinhala='කසුන් පෙරේරා',
            name_with_initials_sinhala='කේ. පෙරේරා',
            dob=date(2018, 1, 1),
            gender='MALE',
            guardian=guardian,
            applied_grade=self.grade1,
            assigned_class=self.section1,
            status='APPROVED'
        )

        # GET delete page shows warning and blocks deletion
        response = self.client.get(reverse('grade_delete', args=[self.grade1.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'මෙම ශ්‍රේණිය මකා දැමිය නොහැක')

        # POST delete is rejected and grade is preserved
        response = self.client.post(reverse('grade_delete', args=[self.grade1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(GradeLevel.objects.filter(id=self.grade1.id).exists())

    # --- Location Allocation Tests ---
    def test_location_allocation_single_and_batch(self):
        self.client.login(username='admin_test', password='password123')

        # Single allocation test
        response = self.client.post(reverse('allocate_grade_location'), {
            'action': 'single_allocation',
            'grade_id': self.grade1.id,
            'classroom_id': self.hall2.id,
        })
        self.assertEqual(response.status_code, 302)
        self.section1.refresh_from_db()
        self.assertEqual(self.section1.classroom, self.hall2)

        # Batch allocation test
        response = self.client.post(reverse('allocate_grade_location'), {
            'action': 'batch_allocation',
            f'classroom_for_grade_{self.grade1.id}': self.hall1.id,
        })
        self.assertEqual(response.status_code, 302)
        self.section1.refresh_from_db()
        self.assertEqual(self.section1.classroom, self.hall1)

    def test_create_and_delete_classroom(self):
        self.client.login(username='principal_test', password='password123')

        # Create new classroom
        response = self.client.post(reverse('create_classroom'), {
            'name': 'නව පුස්තකාල ශාලාව',
            'capacity': 50,
        })
        self.assertEqual(response.status_code, 302)
        new_room = Classroom.objects.filter(name='නව පුස්තකාල ශාලාව').first()
        self.assertIsNotNone(new_room)
        self.assertEqual(new_room.capacity, 50)

        # Delete unused classroom
        response = self.client.post(reverse('delete_classroom', args=[new_room.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Classroom.objects.filter(id=new_room.id).exists())

        # Cannot delete classroom that is currently assigned to a section
        response = self.client.post(reverse('delete_classroom', args=[self.hall1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Classroom.objects.filter(id=self.hall1.id).exists())
