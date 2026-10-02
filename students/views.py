from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Student, Guardian
from .forms import StudentRegistrationForm
from academics.models import GradeLevel, ClassSection, AcademicYear
from accounts.decorators import role_required, teacher_or_staff_required
from teachers.models import TeacherAllocation

def public_register(request):
    """
    Public student self/parent registration form.
    Works smoothly on all mobile devices with Sinhala Unicode support.
    """
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            student = form.save()
            return redirect('registration_success', student_id=student.id)
    else:
        form = StudentRegistrationForm()

    return render(request, 'students/register.html', {'form': form})


def registration_success(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(request, 'students/registration_success.html', {'student': student})


@login_required
def pending_verifications(request):
    """
    Verification queue for pending student applications.
    - Class Teachers can verify applications for their assigned grade(s).
    - Principals & Admins can verify all applications school-wide.
    """
    user = request.user
    is_staff_or_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'PRINCIPAL'])

    if is_staff_or_admin:
        pending_students = Student.objects.filter(status='PENDING').select_related('guardian', 'applied_grade')
    else:
        # Teacher: only see applications for their allocated grades
        teacher_profile = getattr(user, 'teacher_profile', None)
        if not teacher_profile:
            messages.error(request, 'ඔබට ගුරු පැතිකඩක් සම්බන්ධ කර නොමැත.')
            return redirect('dashboard')

        allocated_grade_ids = TeacherAllocation.objects.filter(
            teacher=teacher_profile
        ).values_list('class_section__grade_level_id', flat=True).distinct()

        pending_students = Student.objects.filter(
            status='PENDING',
            applied_grade_id__in=allocated_grade_ids
        ).select_related('guardian', 'applied_grade')

    # Filter by grade if requested
    grade_filter = request.GET.get('grade')
    if grade_filter:
        pending_students = pending_students.filter(applied_grade_id=grade_filter)

    grades = GradeLevel.objects.all().order_by('order_index')

    return render(request, 'students/pending_list.html', {
        'pending_students': pending_students,
        'grades': grades,
        'selected_grade': grade_filter,
    })


@login_required
def verify_student(request, student_id):
    """
    Review and verify a student application.
    Allows entering Admission Number (ඇතුළත් වීමේ අංකය) and assigning Class Section before approval.
    """
    student = get_object_or_404(Student, id=student_id)
    user = request.user
    is_staff_or_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'PRINCIPAL'])

    # Permission check for teachers
    if not is_staff_or_admin:
        teacher_profile = getattr(user, 'teacher_profile', None)
        has_permission = TeacherAllocation.objects.filter(
            teacher=teacher_profile,
            class_section__grade_level=student.applied_grade
        ).exists()
        if not has_permission:
            messages.error(request, 'මෙම ශ්‍රේණියේ සිසුන් අනුමත කිරීමට ඔබට අවසර නොමැත.')
            return redirect('pending_verifications')

    current_year = AcademicYear.objects.filter(is_current=True).first()
    available_sections = ClassSection.objects.filter(
        grade_level=student.applied_grade,
        academic_year=current_year
    )

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'APPROVE':
            admission_no = request.POST.get('admission_number', '').strip()
            section_id = request.POST.get('assigned_class')

            if not admission_no:
                messages.error(request, 'කරුණාකර ඇතුළත් වීමේ අංකය (Admission Number) ඇතුළත් කරන්න.')
                return render(request, 'students/verify_student.html', {
                    'student': student,
                    'available_sections': available_sections
                })

            # Check uniqueness of admission number
            if Student.objects.filter(admission_number=admission_no).exclude(id=student.id).exists():
                messages.error(request, f'"{admission_no}" ඇතුළත් වීමේ අංකය වෙනත් ශිෂ්‍යයෙකු සඳහා දැනටමත් භාවිත කර ඇත.')
                return render(request, 'students/verify_student.html', {
                    'student': student,
                    'available_sections': available_sections
                })

            student.admission_number = admission_no
            if section_id:
                student.assigned_class_id = section_id
            student.status = 'APPROVED'
            student.verified_by = user
            student.verified_at = timezone.now()
            student.save()

            messages.success(request, f'ශිෂ්‍ය {student.name_with_initials_sinhala} සාර්ථකව අනුමත කර පන්තියට ඇතුළත් කරන ලදී.')
            return redirect('pending_verifications')

        elif action == 'REJECT':
            student.status = 'REJECTED'
            student.verified_by = user
            student.verified_at = timezone.now()
            student.save()
            messages.info(request, f'අයදුම්පත ප්‍රතික්ෂේප කරන ලදී.')
            return redirect('pending_verifications')

    return render(request, 'students/verify_student.html', {
        'student': student,
        'available_sections': available_sections,
    })


@login_required
def student_list(request):
    """
    List of active/all students.
    - Teachers see their class students (or all if principal/admin).
    """
    user = request.user
    is_staff_or_admin = user.is_superuser or (hasattr(user, 'profile') and user.profile.role in ['ADMIN', 'PRINCIPAL'])

    query = request.GET.get('q', '').strip()
    grade_id = request.GET.get('grade')
    status_filter = request.GET.get('status', 'APPROVED')

    if is_staff_or_admin:
        students = Student.objects.all()
    else:
        teacher_profile = getattr(user, 'teacher_profile', None)
        if not teacher_profile:
            messages.error(request, 'ගුරු පැතිකඩක් සොයා ගැනීමට නොහැකි විය.')
            return redirect('dashboard')
        allocated_sections = TeacherAllocation.objects.filter(
            teacher=teacher_profile
        ).values_list('class_section_id', flat=True)
        students = Student.objects.filter(assigned_class_id__in=allocated_sections)

    if status_filter:
        students = students.filter(status=status_filter)

    if grade_id:
        students = students.filter(applied_grade_id=grade_id)

    if query:
        students = students.filter(
            Q(full_name_sinhala__icontains=query) |
            Q(name_with_initials_sinhala__icontains=query) |
            Q(admission_number__icontains=query) |
            Q(guardian__primary_phone__icontains=query)
        )

    students = students.select_related('guardian', 'applied_grade', 'assigned_class')
    grades = GradeLevel.objects.all().order_by('order_index')

    return render(request, 'students/student_list.html', {
        'students': students,
        'grades': grades,
        'query': query,
        'selected_grade': grade_id,
        'selected_status': status_filter,
    })


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.select_related('guardian', 'applied_grade', 'assigned_class'), id=student_id)
    # Siblings in the same school (shared guardian)
    siblings = Student.objects.filter(guardian=student.guardian).exclude(id=student.id)
    # Attendance records
    attendance_records = student.attendance_records.select_related('session').order_by('-session__date')[:15]
    total_attended = student.attendance_records.filter(status='PRESENT').count()
    total_sessions = student.attendance_records.count()
    attendance_rate = round((total_attended / total_sessions * 100), 1) if total_sessions > 0 else 0

    return render(request, 'students/student_detail.html', {
        'student': student,
        'siblings': siblings,
        'attendance_records': attendance_records,
        'total_attended': total_attended,
        'total_sessions': total_sessions,
        'attendance_rate': attendance_rate,
    })
