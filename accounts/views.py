from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .forms import UserPasswordChangeForm
from students.models import Student
from teachers.models import Teacher, TeacherAllocation
from academics.models import ClassSection, AcademicYear, GradeLevel
from attendance.models import SundaySession, AttendanceRecord
from datetime import date

def home_view(request):
    current_year = AcademicYear.objects.filter(is_current=True).first()
    grades = GradeLevel.objects.all().order_by('order_index')
    return render(request, 'home.html', {
        'current_year': current_year,
        'grades': grades,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '').strip()
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f'සාදරයෙන් පිළිගනිමු, {user.first_name or user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'පරිශීලක නාමය හෝ මුරපදය වැරදිය. කරුණාකර නැවත උත්සාහ කරන්න.')

    teachers = Teacher.objects.filter(is_active=True, user__isnull=False).select_related('user').prefetch_related('allocations__class_section__grade_level').order_by('user__username')
    return render(request, 'accounts/login.html', {'teachers': teachers})


def logout_view(request):
    logout(request)
    messages.info(request, 'ඔබ සාර්ථකව පද්ධතියෙන් ඉවත් විය.')
    return redirect('login')


@login_required
def change_password_view(request):
    """
    Allows any authenticated user to change their account password.
    Updates the session auth hash so the user remains logged in.
    """
    if request.method == 'POST':
        form = UserPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'ඔබගේ මුරපදය සාර්ථකව වෙනස් කරන ලදී! (Your password has been changed successfully!)')
            return redirect('dashboard')
        else:
            messages.error(request, 'මුරපදය වෙනස් කිරීම අසාර්ථක විය. කරුණාකර පහත දෝෂ පරීක්ෂා කර නැවත උත්සාහ කරන්න.')
    else:
        form = UserPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {
        'form': form,
    })


@login_required
def dashboard(request):
    user = request.user
    role = 'TEACHER'
    if user.is_superuser:
        role = 'ADMIN'
    elif hasattr(user, 'profile'):
        role = user.profile.role

    current_year = AcademicYear.objects.filter(is_current=True).first()

    if role in ['ADMIN', 'PRINCIPAL']:
        # Admin / Principal Dashboard
        total_students = Student.objects.filter(status='APPROVED').count()
        pending_count = Student.objects.filter(status='PENDING').count()
        total_teachers = Teacher.objects.filter(is_active=True).count()
        
        # Class sections with student counts
        classes = ClassSection.objects.filter(
            academic_year=current_year
        ).select_related('grade_level', 'classroom').prefetch_related(
            'teacher_allocations__teacher',
            'students'
        )

        class_summaries = []
        for cs in classes:
            student_count = cs.students.filter(status='APPROVED').count()
            class_teacher_alloc = cs.teacher_allocations.filter(is_class_teacher=True).first()
            subject_allocs = cs.teacher_allocations.filter(is_class_teacher=False)
            class_summaries.append({
                'section': cs,
                'student_count': student_count,
                'class_teacher': class_teacher_alloc.teacher if class_teacher_alloc else None,
                'subject_allocs': subject_allocs,
            })

        # Recent pending applications
        recent_pending = Student.objects.filter(status='PENDING').select_related('guardian', 'applied_grade')[:5]

        return render(request, 'accounts/admin_dashboard.html', {
            'role': role,
            'total_students': total_students,
            'pending_count': pending_count,
            'total_teachers': total_teachers,
            'current_year': current_year,
            'class_summaries': class_summaries,
            'recent_pending': recent_pending,
        })

    else:
        # Teacher Dashboard
        teacher_profile = getattr(user, 'teacher_profile', None)
        if not teacher_profile:
            messages.warning(request, 'ඔබගේ ගිණුමට තවමත් ගුරු පැතිකඩක් සම්බන්ධ කර නොමැත. කරුණාකර ප්‍රධානාචාර්යතුමන් අමතන්න.')
            return render(request, 'accounts/teacher_dashboard.html', {'teacher': None})

        # Allocated classes
        allocations = TeacherAllocation.objects.filter(
            teacher=teacher_profile,
            class_section__academic_year=current_year
        ).select_related('class_section', 'class_section__grade_level', 'class_section__classroom')

        # Grades allocated to this teacher
        allocated_grade_ids = [a.class_section.grade_level_id for a in allocations]

        # Pending applications for this teacher's grades
        pending_for_teacher = Student.objects.filter(
            status='PENDING',
            applied_grade_id__in=allocated_grade_ids
        ).select_related('guardian', 'applied_grade')

        class_details = []
        for alloc in allocations:
            cs = alloc.class_section
            students = cs.students.filter(status='APPROVED').select_related('guardian')
            class_details.append({
                'allocation': alloc,
                'class_section': cs,
                'students': students,
                'student_count': students.count(),
            })

        return render(request, 'accounts/teacher_dashboard.html', {
            'teacher': teacher_profile,
            'class_details': class_details,
            'pending_for_teacher': pending_for_teacher,
            'pending_count': pending_for_teacher.count(),
            'current_year': current_year,
        })
