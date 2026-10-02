from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from academics.models import GradeLevel, AcademicYear, ClassSection
from teachers.models import Teacher, TeacherAllocation
from students.models import Student, Guardian
from datetime import date

class DahamPasalaTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Academic year & grade
        self.year = AcademicYear.objects.create(year=2026, is_current=True)
        self.grade1 = GradeLevel.objects.create(order_index=1, name='1 ශ්‍රේණිය', english_name='Grade 1')
        self.grade4 = GradeLevel.objects.create(order_index=4, name='4 ශ්‍රේණිය', english_name='Grade 4')

        self.section1 = ClassSection.objects.create(
            grade_level=self.grade1,
            academic_year=self.year,
            section_name='ප්‍රධාන'
        )

        # Admin user
        self.admin_user = User.objects.create_superuser(username='test_admin', password='password123')
        UserProfile.objects.create(user=self.admin_user, role='ADMIN')

        # Principal user
        self.principal_user = User.objects.create_user(username='test_principal', password='password123')
        UserProfile.objects.create(user=self.principal_user, role='PRINCIPAL')

        # Teacher user & profile
        self.teacher_user = User.objects.create_user(username='test_teacher1', password='password123')
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            full_name_sinhala='කේ. ඩී. ගයාන් පෙරේරා',
            name_with_initials='කේ. ඩී. ජී. පෙරේරා',
            phone='0711112233',
            is_active=True
        )

        # Allocate teacher to grade 1
        TeacherAllocation.objects.create(
            teacher=self.teacher,
            class_section=self.section1,
            subject='බුද්ධ ධර්මය',
            is_class_teacher=True
        )

    def test_public_registration_sinhala_and_normalization(self):
        """Test registering two siblings with the same phone number normalizes into 1 Guardian record"""
        # Sibling 1
        data1 = {
            'full_name_sinhala': 'එම්. ඩී. සසිඳු තේජාන්',
            'name_with_initials_sinhala': 'එම්. ඩී. එස්. තේජාන්',
            'dob': '2020-03-15',
            'gender': 'MALE',
            'applied_grade': self.grade1.id,
            'guardian_name': 'එම්. ඩී. සුනිල් ශාන්ත',
            'relationship_to_guardian': 'FATHER',
            'guardian_phone': '0778899001',
            'guardian_whatsapp': '0778899001',
            'guardian_address': 'නො. 12/බී, පන්සල පාර',
        }
        res1 = self.client.post(reverse('public_register'), data1)
        self.assertEqual(res1.status_code, 302)

        # Sibling 2 (different grade, same guardian phone)
        data2 = {
            'full_name_sinhala': 'එම්. ඩී. දසුනි නෙත්මිනා',
            'name_with_initials_sinhala': 'එම්. ඩී. ඩී. නෙත්මිනා',
            'dob': '2017-07-20',
            'gender': 'FEMALE',
            'applied_grade': self.grade4.id,
            'guardian_name': 'එම්. ඩී. සුනිල් ශාන්ත',
            'relationship_to_guardian': 'FATHER',
            'guardian_phone': '0778899001',
            'guardian_whatsapp': '0778899001',
            'guardian_address': 'නො. 12/බී, පන්සල පාර',
        }
        res2 = self.client.post(reverse('public_register'), data2)
        self.assertEqual(res2.status_code, 302)

        # Verify only 1 guardian exists (3NF normalization)
        self.assertEqual(Guardian.objects.count(), 1)
        guardian = Guardian.objects.get(primary_phone='0778899001')
        self.assertEqual(guardian.students.count(), 2)

        # Both students should be in PENDING status
        s1 = Student.objects.get(name_with_initials_sinhala='එම්. ඩී. එස්. තේජාන්')
        s2 = Student.objects.get(name_with_initials_sinhala='එම්. ඩී. ඩී. නෙත්මිනා')
        self.assertEqual(s1.status, 'PENDING')
        self.assertEqual(s2.status, 'PENDING')

    def test_teacher_child_registration_link(self):
        """Test teacher registering their child correctly links to Teacher model"""
        data = {
            'full_name_sinhala': 'කේ. ඩී. සිනෙත් ප්‍රභාෂ්වර',
            'name_with_initials_sinhala': 'කේ. ඩී. එස්. ප්‍රභාෂ්වර',
            'dob': '2020-05-10',
            'gender': 'MALE',
            'applied_grade': self.grade1.id,
            'guardian_name': self.teacher.full_name_sinhala,
            'relationship_to_guardian': 'FATHER',
            'guardian_phone': self.teacher.phone,
            'guardian_address': 'ගුරු නිවස',
            'is_teacher_child': True,
            'linked_teacher': self.teacher.id,
        }
        res = self.client.post(reverse('public_register'), data)
        self.assertEqual(res.status_code, 302)

        student = Student.objects.get(name_with_initials_sinhala='කේ. ඩී. එස්. ප්‍රභාෂ්වර')
        self.assertEqual(student.guardian.linked_teacher, self.teacher)

    def test_verification_permissions(self):
        """Test that teacher can only verify student for their assigned grade, while principal can verify any"""
        # Create student for grade 1 and student for grade 4
        guardian = Guardian.objects.create(
            full_name_sinhala='පියසිරි පෙරේරා',
            primary_phone='0712345678',
            address='ලිපිනය'
        )
        s_g1 = Student.objects.create(
            full_name_sinhala='ළමයා 1',
            name_with_initials_sinhala='ළමයා 1',
            dob=date(2020, 1, 1),
            gender='MALE',
            guardian=guardian,
            applied_grade=self.grade1,
            status='PENDING'
        )
        s_g4 = Student.objects.create(
            full_name_sinhala='ළමයා 4',
            name_with_initials_sinhala='ළමයා 4',
            dob=date(2017, 1, 1),
            gender='MALE',
            guardian=guardian,
            applied_grade=self.grade4,
            status='PENDING'
        )

        # Login as teacher allocated only to grade 1
        self.client.login(username='test_teacher1', password='password123')

        # Teacher should be able to verify Grade 1
        res1 = self.client.post(reverse('verify_student', args=[s_g1.id]), {
            'action': 'APPROVE',
            'admission_number': 'DP/2026/010',
            'assigned_class': self.section1.id
        })
        self.assertEqual(res1.status_code, 302)
        s_g1.refresh_from_db()
        self.assertEqual(s_g1.status, 'APPROVED')
        self.assertEqual(s_g1.admission_number, 'DP/2026/010')
        self.assertEqual(s_g1.verified_by, self.teacher_user)

        # Teacher should NOT have permission to verify Grade 4
        res2 = self.client.post(reverse('verify_student', args=[s_g4.id]), {
            'action': 'APPROVE',
            'admission_number': 'DP/2026/020',
        })
        s_g4.refresh_from_db()
        self.assertEqual(s_g4.status, 'PENDING') # unchanged

        # Principal logs in and CAN verify Grade 4
        self.client.logout()
        self.client.login(username='test_principal', password='password123')
        res3 = self.client.post(reverse('verify_student', args=[s_g4.id]), {
            'action': 'APPROVE',
            'admission_number': 'DP/2026/020',
        })
        self.assertEqual(res3.status_code, 302)
        s_g4.refresh_from_db()
        self.assertEqual(s_g4.status, 'APPROVED')
        self.assertEqual(s_g4.verified_by, self.principal_user)
