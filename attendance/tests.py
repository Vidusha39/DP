from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile
from academics.models import GradeLevel, AcademicYear, ClassSection
from teachers.models import Teacher, TeacherAllocation
from students.models import Student, Guardian
from attendance.models import SundaySession, AttendanceRecord
from datetime import date

class AttendanceTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.year = AcademicYear.objects.create(year=2026, is_current=True)
        self.grade1 = GradeLevel.objects.create(order_index=1, name='1 ශ්‍රේණිය', english_name='Grade 1')
        self.section1 = ClassSection.objects.create(
            grade_level=self.grade1,
            academic_year=self.year,
            section_name='ප්‍රධාන'
        )

        self.teacher_user = User.objects.create_user(username='test_teacher', password='password123')
        UserProfile.objects.create(user=self.teacher_user, role='TEACHER')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            full_name_sinhala='කේ. ඩී. ගයාන් පෙරේරා',
            name_with_initials='කේ. ඩී. ජී. පෙරේරා',
            phone='0711112233',
            is_active=True
        )
        TeacherAllocation.objects.create(
            teacher=self.teacher,
            class_section=self.section1,
            subject='බුද්ධ ධර්මය',
            is_class_teacher=True
        )

        self.guardian = Guardian.objects.create(
            full_name_sinhala='සුනිල් පෙරේරා',
            primary_phone='0771234567',
            address='ලිපිනය'
        )
        self.student = Student.objects.create(
            admission_number='2026/001',
            full_name_sinhala='කසුන් පෙරේරා',
            name_with_initials_sinhala='කේ. පෙරේරා',
            dob=date(2020, 1, 1),
            gender='MALE',
            guardian=self.guardian,
            applied_grade=self.grade1,
            assigned_class=self.section1,
            status='APPROVED'
        )

    def test_teacher_mark_attendance(self):
        self.client.login(username='test_teacher', password='password123')
        today_str = date.today().isoformat()
        
        post_data = {
            f'status_{self.student.id}': 'PRESENT'
        }
        res = self.client.post(
            f"{reverse('mark_attendance', args=[self.section1.id])}?date={today_str}", 
            post_data
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(AttendanceRecord.objects.count(), 1)
        record = AttendanceRecord.objects.first()
        self.assertEqual(record.status, 'PRESENT')
        self.assertEqual(record.marked_by, self.teacher_user)

    def test_excel_export(self):
        self.client.login(username='test_teacher', password='password123')
        res = self.client.get(reverse('export_excel', args=[self.section1.id]))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertTrue(len(res.content) > 0)
