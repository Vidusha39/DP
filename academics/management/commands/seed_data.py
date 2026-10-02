from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from academics.models import GradeLevel, AcademicYear, Classroom, ClassSection
from teachers.models import Teacher, TeacherAllocation
from students.models import Guardian, Student
from datetime import date

class Command(BaseCommand):
    help = 'Populates initial standard Daham Pasala grades, classrooms, class sections, and initial accounts (admin, principal, teacher1).'

    def handle(self, *args, **options):
        self.stdout.write("Initializing Daham Pasala standard data...")

        # 1. Academic Year
        academic_year, _ = AcademicYear.objects.get_or_create(
            year=2026,
            defaults={'is_current': True}
        )
        self.stdout.write(self.style.SUCCESS(f"Academic Year 2026 ready."))

        # 2. Grade Levels (1 to 11, Final, Dharmacharya)
        grades_data = [
            (1, "1 ශ්‍රේණිය", "Grade 1"),
            (2, "2 ශ්‍රේණිය", "Grade 2"),
            (3, "3 ශ්‍රේණිය", "Grade 3"),
            (4, "4 ශ්‍රේණිය", "Grade 4"),
            (5, "5 ශ්‍රේණිය", "Grade 5"),
            (6, "6 ශ්‍රේණිය", "Grade 6"),
            (7, "7 ශ්‍රේණිය", "Grade 7"),
            (8, "8 ශ්‍රේණිය", "Grade 8"),
            (9, "9 ශ්‍රේණිය", "Grade 9"),
            (10, "10 ශ්‍රේණිය", "Grade 10"),
            (11, "11 ශ්‍රේණිය", "Grade 11"),
            (12, "අවසාන ශ්‍රේණිය", "Final Grade"),
            (13, "ධර්මාචාර්ය", "Dharmacharya"),
        ]

        grade_objs = {}
        for order, name, eng in grades_data:
            grade, _ = GradeLevel.objects.get_or_create(
                order_index=order,
                defaults={'name': name, 'english_name': eng}
            )
            # Update name if changed
            grade.name = name
            grade.english_name = eng
            grade.save()
            grade_objs[order] = grade
        self.stdout.write(self.style.SUCCESS(f"Loaded {len(grade_objs)} Daham Pasala grade levels."))

        # 3. Classrooms
        rooms_data = [
            ("ප්‍රධාන ධර්ම ශාලාව", 100),
            ("1 වන ගොඩනැගිල්ල - කාමර අංක 01", 35),
            ("1 වන ගොඩනැගිල්ල - කාමර අංක 02", 35),
            ("2 වන ගොඩනැගිල්ල - කාමර අංක 01", 40),
        ]
        classrooms = []
        for r_name, cap in rooms_data:
            room, _ = Classroom.objects.get_or_create(name=r_name, defaults={'capacity': cap})
            classrooms.append(room)

        # 4. Class Sections for 2026
        for order, grade in grade_objs.items():
            assigned_room = classrooms[min(order - 1, len(classrooms) - 1)] if classrooms else None
            ClassSection.objects.get_or_create(
                grade_level=grade,
                academic_year=academic_year,
                section_name='ප්‍රධාන',
                defaults={'classroom': assigned_room}
            )
        self.stdout.write(self.style.SUCCESS("Created class sections for 2026."))

        # 5. Accounts: Admin (admin / admin123)
        admin_user, created = User.objects.get_or_create(username='admin')
        admin_user.set_password('admin123')
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.first_name = "පද්ධති"
        admin_user.last_name = "පරිපාලක"
        admin_user.save()
        UserProfile.objects.update_or_create(
            user=admin_user,
            defaults={'role': 'ADMIN', 'phone': '0771234567'}
        )
        self.stdout.write(self.style.SUCCESS("Admin account created: admin / admin123"))

        # Principal (principal / principal123)
        principal_user, created = User.objects.get_or_create(username='principal')
        principal_user.set_password('principal123')
        principal_user.is_staff = True
        principal_user.first_name = "පූජ්‍ය ධම්මරතන"
        principal_user.last_name = "හිමි (ප්‍රධානාචාර්ය)"
        principal_user.save()
        UserProfile.objects.update_or_create(
            user=principal_user,
            defaults={'role': 'PRINCIPAL', 'phone': '0719876543'}
        )
        self.stdout.write(self.style.SUCCESS("Principal account created: principal / principal123"))

        # Teacher 1 (teacher1 / teacher123)
        teacher_user, created = User.objects.get_or_create(username='teacher1')
        teacher_user.set_password('teacher123')
        teacher_user.first_name = "ගයාන්"
        teacher_user.last_name = "පෙරේරා"
        teacher_user.save()
        UserProfile.objects.update_or_create(
            user=teacher_user,
            defaults={'role': 'TEACHER', 'phone': '0754433221'}
        )

        teacher_profile, _ = Teacher.objects.update_or_create(
            user=teacher_user,
            defaults={
                'title': 'MR',
                'full_name_sinhala': 'කේ. ඩී. ගයාන් පෙරේරා',
                'name_with_initials': 'කේ. ඩී. ජී. පෙරේරා',
                'phone': '0754433221',
                'whatsapp_phone': '0754433221',
                'address': 'නො. 45, විහාර මාවත, නගරය',
                'qualifications': 'ධර්මාචාර්ය විභාගය සම්මාන සාමාර්ථ, BA (Kelaniya)',
                'date_joined': date(2022, 1, 1),
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS("Teacher account created: teacher1 / teacher123"))

        # Allocate teacher1 as Class Teacher to 1 ශ්‍රේණිය
        grade1_section = ClassSection.objects.get(grade_level=grade_objs[1], academic_year=academic_year)
        TeacherAllocation.objects.get_or_create(
            teacher=teacher_profile,
            class_section=grade1_section,
            subject='බුද්ධ ධර්මය',
            defaults={'is_class_teacher': True}
        )
        self.stdout.write(self.style.SUCCESS("Allocated teacher1 to Grade 1 section."))

        # 6. Sample Guardian and Students to showcase 1-to-many & teacher-child link
        # Family 1: Regular Guardian with 2 children (Grade 1 & Grade 4)
        g1, _ = Guardian.objects.get_or_create(
            primary_phone='0778899001',
            defaults={
                'full_name_sinhala': 'එම්. ඩී. සුනිල් ශාන්ත',
                'whatsapp_phone': '0778899001',
                'address': 'නො. 12/බී, පන්සල පාර, අලව්ව',
                'occupation': 'ව්‍යාපාරික'
            }
        )
        
        # Child 1 in Grade 1 (Active)
        Student.objects.get_or_create(
            admission_number='2026/001',
            defaults={
                'full_name_sinhala': 'එම්. ඩී. සසිඳු තේජාන් ශාන්ත',
                'name_with_initials_sinhala': 'එම්. ඩී. එස්. ටී. ශාන්ත',
                'dob': date(2020, 3, 15),
                'gender': 'MALE',
                'guardian': g1,
                'relationship_to_guardian': 'FATHER',
                'applied_grade': grade_objs[1],
                'assigned_class': grade1_section,
                'status': 'APPROVED',
                'verified_by': admin_user,
            }
        )

        # Child 2 in Grade 4 (Pending application to test approval flow)
        Student.objects.get_or_create(
            full_name_sinhala='එම්. ඩී. දසුනි නෙත්මිනා ශාන්ත',
            name_with_initials_sinhala='එම්. ඩී. ඩී. එන්. ශාන්ත',
            defaults={
                'dob': date(2017, 7, 20),
                'gender': 'FEMALE',
                'guardian': g1,
                'relationship_to_guardian': 'FATHER',
                'applied_grade': grade_objs[4],
                'status': 'PENDING',  # Waiting for verification!
            }
        )

        # Family 2: Teacher's own child! Demonstrates normalized teacher link
        teacher_guardian, _ = Guardian.objects.get_or_create(
            primary_phone=teacher_profile.phone,
            defaults={
                'full_name_sinhala': teacher_profile.full_name_sinhala,
                'whatsapp_phone': teacher_profile.whatsapp_phone,
                'address': teacher_profile.address,
                'occupation': 'දහම් පාසල් ආචාර්ය',
                'linked_teacher': teacher_profile,
            }
        )
        Student.objects.get_or_create(
            admission_number='2026/002',
            defaults={
                'full_name_sinhala': 'කේ. ඩී. සිනෙත් ප්‍රභාෂ්වර පෙරේරා',
                'name_with_initials_sinhala': 'කේ. ඩී. එස්. පී. පෙරේරා',
                'dob': date(2020, 5, 10),
                'gender': 'MALE',
                'guardian': teacher_guardian,
                'relationship_to_guardian': 'FATHER',
                'applied_grade': grade_objs[1],
                'assigned_class': grade1_section,
                'status': 'APPROVED',
                'verified_by': principal_user,
            }
        )

        self.stdout.write(self.style.SUCCESS("Seeded sample students and guardians (including teacher child)."))
        self.stdout.write(self.style.SUCCESS("Initialization complete!"))

