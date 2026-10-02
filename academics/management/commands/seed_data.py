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
        # Teachers (teacher1 to teacher13 / teacher123) for every grade (1 to 13)
        teachers_seed_info = [
            {
                'order': 1,
                'username': 'teacher1',
                'title': 'MR',
                'first_name': 'ගයාන්',
                'last_name': 'පෙරේරා',
                'full_name': 'කේ. ඩී. ගයාන් පෙරේරා',
                'initials': 'කේ. ඩී. ජී. පෙරේරා',
                'phone': '0754433221',
                'qualifications': 'ධර්මාචාර්ය විභාගය සම්මාන සාමාර්ථ, BA (Kelaniya)',
            },
            {
                'order': 2,
                'username': 'teacher2',
                'title': 'MRS',
                'first_name': 'නිලන්ති',
                'last_name': 'කුමාරි',
                'full_name': 'ඩබ්ලිව්. ඒ. නිලන්ති කුමාරි',
                'initials': 'ඩබ්ලිව්. ඒ. එන්. කුමාරි',
                'phone': '0712345602',
                'qualifications': 'පෙර පාසල් ඩිප්ලෝමාව, ධර්මාචාර්ය',
            },
            {
                'order': 3,
                'username': 'teacher3',
                'title': 'MR',
                'first_name': 'චාමින්ද',
                'last_name': 'කුමාර',
                'full_name': 'එච්. එම්. චාමින්ද කුමාර',
                'initials': 'එච්. එම්. සී. කුමාර',
                'phone': '0712345603',
                'qualifications': 'ධර්මාචාර්ය, ශාස්ත්‍රවේදී උපාධිය',
            },
            {
                'order': 4,
                'username': 'teacher4',
                'title': 'MRS',
                'first_name': 'සුනේත්‍රා',
                'last_name': 'රත්නායක',
                'full_name': 'ආර්. ඩී. සුනේත්‍රා රත්නායක',
                'initials': 'ආර්. ඩී. එස්. රත්නායක',
                'phone': '0712345604',
                'qualifications': 'ගුරු පුහුණු ඩිප්ලෝමාව, ධර්මාචාර්ය',
            },
            {
                'order': 5,
                'username': 'teacher5',
                'title': 'VEN',
                'first_name': 'තිස්ස',
                'last_name': 'හිමි',
                'full_name': 'පූජ්‍ය මීගහවෙල තිස්ස හිමි',
                'initials': 'පූජ්‍ය එම්. තිස්ස හිමි',
                'phone': '0712345605',
                'qualifications': 'ප්‍රාචීන ප්‍රාරම්භ, ධර්මාචාර්ය',
            },
            {
                'order': 6,
                'username': 'teacher6',
                'title': 'MISS',
                'first_name': 'පියුමි',
                'last_name': 'හංසිකා',
                'full_name': 'කේ. ඒ. පියුමි හංසිකා',
                'initials': 'කේ. ඒ. පී. හංසිකා',
                'phone': '0712345606',
                'qualifications': 'B.Sc. (Hons), ධර්මාචාර්ය විභාගය',
            },
            {
                'order': 7,
                'username': 'teacher7',
                'title': 'MR',
                'first_name': 'රංජිත්',
                'last_name': 'ප්‍රනාන්දු',
                'full_name': 'එස්. පී. රංජිත් ප්‍රනාන්දු',
                'initials': 'එස්. පී. ආර්. ප්‍රනාන්දු',
                'phone': '0712345607',
                'qualifications': 'ධර්මාචාර්ය, අධ්‍යාපන ඩිප්ලෝමා',
            },
            {
                'order': 8,
                'username': 'teacher8',
                'title': 'MRS',
                'first_name': 'සුජාතා',
                'last_name': 'දිසානායක',
                'full_name': 'එම්. කේ. සුජාතා දිසානායක',
                'initials': 'එම්. කේ. එස්. දිසානායක',
                'phone': '0712345608',
                'qualifications': 'BA (Kelaniya), ධර්මාචාර්ය',
            },
            {
                'order': 9,
                'username': 'teacher9',
                'title': 'VEN',
                'first_name': 'සුමංගල',
                'last_name': 'හිමි',
                'full_name': 'පූජ්‍ය රජගිරි සුමංගල හිමි',
                'initials': 'පූජ්‍ය ආර්. සුමංගල හිමි',
                'phone': '0712345609',
                'qualifications': 'ප්‍රාචීන මධ්‍යම, රාජකීය පණ්ඩිත',
            },
            {
                'order': 10,
                'username': 'teacher10',
                'title': 'MR',
                'first_name': 'ලක්ෂ්මන්',
                'last_name': 'ජයවර්ධන',
                'full_name': 'බී. එම්. ලක්ෂ්මන් ජයවර්ධන',
                'initials': 'බී. එම්. එල්. ජයවර්ධන',
                'phone': '0712345610',
                'qualifications': 'ධර්මාචාර්ය, විශ්‍රාමික විදුහල්පති',
            },
            {
                'order': 11,
                'username': 'teacher11',
                'title': 'MRS',
                'first_name': 'මල්කාන්ති',
                'last_name': 'සේනාරත්න',
                'full_name': 'ඩී. ජී. මල්කාන්ති සේනාරත්න',
                'initials': 'ඩී. ජී. එම්. සේනාරත්න',
                'phone': '0712345611',
                'qualifications': 'ධර්මාචාර්ය සම්මාන, MA (BPU)',
            },
            {
                'order': 12,
                'username': 'teacher12',
                'title': 'VEN',
                'first_name': 'ආනන්ද',
                'last_name': 'හිමි',
                'full_name': 'පූජ්‍ය බෙල්ලන ආනන්ද හිමි',
                'initials': 'පූජ්‍ය බී. ආනන්ද හිමි',
                'phone': '0712345612',
                'qualifications': 'රාජකීය පණ්ඩිත, MA (Pali & Buddhist)',
            },
            {
                'order': 13,
                'username': 'teacher13',
                'title': 'MR',
                'first_name': 'සෝමසිරි',
                'last_name': 'විජේතුංග',
                'full_name': 'එන්. එස්. සෝමසිරි විජේතුංග',
                'initials': 'එන්. එස්. එස්. විජේතුංග',
                'phone': '0712345613',
                'qualifications': 'ධර්මාචාර්ය ප්‍රවීණ, BA Hons (Buddhist Studies)',
            },
        ]

        teacher_objs = {}
        for t_info in teachers_seed_info:
            t_user, _ = User.objects.get_or_create(username=t_info['username'])
            t_user.set_password('teacher123')
            t_user.first_name = t_info['first_name']
            t_user.last_name = t_info['last_name']
            t_user.save()

            UserProfile.objects.update_or_create(
                user=t_user,
                defaults={'role': 'TEACHER', 'phone': t_info['phone']}
            )

            t_profile, _ = Teacher.objects.update_or_create(
                user=t_user,
                defaults={
                    'title': t_info['title'],
                    'full_name_sinhala': t_info['full_name'],
                    'name_with_initials': t_info['initials'],
                    'phone': t_info['phone'],
                    'whatsapp_phone': t_info['phone'],
                    'address': 'නො. 45, විහාර මාවත',
                    'qualifications': t_info['qualifications'],
                    'date_joined': date(2022, 1, 1),
                    'is_active': True,
                }
            )
            teacher_objs[t_info['order']] = t_profile

            # Allocate as Class Teacher to respective grade
            grade_sec = ClassSection.objects.filter(grade_level=grade_objs[t_info['order']], academic_year=academic_year).first()
            if grade_sec:
                TeacherAllocation.objects.update_or_create(
                    teacher=t_profile,
                    class_section=grade_sec,
                    subject='බුද්ධ ධර්මය',
                    defaults={'is_class_teacher': True}
                )

        teacher_profile = teacher_objs[1]
        grade1_section = ClassSection.objects.get(grade_level=grade_objs[1], academic_year=academic_year)
        self.stdout.write(self.style.SUCCESS(f"Created {len(teacher_objs)} Teacher accounts: teacher1 to teacher{len(teacher_objs)} (Password: teacher123)"))

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

