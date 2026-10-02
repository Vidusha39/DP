from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Teacher, TeacherAllocation
from accounts.models import UserProfile
from accounts.decorators import principal_or_admin_required
from academics.models import ClassSection, AcademicYear

@login_required
@principal_or_admin_required
def teacher_list(request):
    teachers = Teacher.objects.all().select_related('user').prefetch_related('allocations__class_section', 'allocations__class_section__grade_level')
    return render(request, 'teachers/teacher_list.html', {'teachers': teachers})


@login_required
@principal_or_admin_required
def create_teacher(request):
    """
    Principal or Admin can create a new Teacher account and profile.
    Automatically suggests the next teacher username and default password.
    """
    next_idx = Teacher.objects.count() + 1
    suggested_username = f"teacher{next_idx}"
    while User.objects.filter(username=suggested_username).exists():
        next_idx += 1
        suggested_username = f"teacher{next_idx}"

    context = {
        'suggested_username': suggested_username,
        'default_password': 'teacher123'
    }

    if request.method == 'POST':
        username = request.POST.get('username', '').strip() or suggested_username
        password = request.POST.get('password', '').strip() or 'teacher123'
        title = request.POST.get('title', 'MR')
        full_name = request.POST.get('full_name', '').strip()
        name_initials = request.POST.get('name_initials', '').strip()
        phone = request.POST.get('phone', '').strip()
        whatsapp = request.POST.get('whatsapp', '').strip()
        address = request.POST.get('address', '').strip()
        qualifications = request.POST.get('qualifications', '').strip()

        if not username or not password or not full_name or not phone:
            messages.error(request, 'කරුණාකර අවශ්‍ය සියලු තොරතුරු ඇතුළත් කරන්න.')
            return render(request, 'teachers/teacher_form.html', context)

        if User.objects.filter(username=username).exists():
            messages.error(request, f'"{username}" පරිශීලක නාමය දැනටමත් භාවිතයේ පවතී.')
            return render(request, 'teachers/teacher_form.html', context)

        # Create auth User
        user = User.objects.create_user(username=username, password=password)
        user.first_name = name_initials
        user.save()

        # Create UserProfile with TEACHER role
        UserProfile.objects.create(user=user, role='TEACHER', phone=phone)

        # Create Teacher record
        teacher = Teacher.objects.create(
            user=user,
            title=title,
            full_name_sinhala=full_name,
            name_with_initials=name_initials,
            phone=phone,
            whatsapp_phone=whatsapp or phone,
            address=address,
            qualifications=qualifications,
        )

        messages.success(request, f'ගුරුභවතා {teacher.display_name} සාර්ථකව පද්ධතියට එක් කරන ලදී. (Username: {username} | මුරපදය: {password})')
        return redirect('teacher_list')

    return render(request, 'teachers/teacher_form.html', context)


@login_required
@principal_or_admin_required
def allocate_teacher(request):
    """
    Assign a teacher to a class section and subject.
    """
    current_year = AcademicYear.objects.filter(is_current=True).first()
    teachers = Teacher.objects.filter(is_active=True)
    class_sections = ClassSection.objects.filter(academic_year=current_year).select_related('grade_level')
    existing_allocations = TeacherAllocation.objects.filter(
        class_section__academic_year=current_year
    ).select_related('teacher', 'class_section', 'class_section__grade_level')

    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        section_id = request.POST.get('class_section_id')
        subject = request.POST.get('subject', 'බුද්ධ ධර්මය').strip()
        is_class_teacher = request.POST.get('is_class_teacher') == 'on'

        if teacher_id and section_id and subject:
            teacher = get_object_or_404(Teacher, id=teacher_id)
            section = get_object_or_404(ClassSection, id=section_id)

            alloc, created = TeacherAllocation.objects.update_or_create(
                teacher=teacher,
                class_section=section,
                subject=subject,
                defaults={'is_class_teacher': is_class_teacher}
            )
            messages.success(request, f'{teacher.display_name} සාර්ථකව {section.grade_level.name} පන්තියට ({subject}) අනුයුක්ත කරන ලදී.')
            return redirect('allocate_teacher')
        else:
            messages.error(request, 'කරුණාකර සියලු විස්තර තෝරන්න.')

    return render(request, 'teachers/allocate_form.html', {
        'teachers': teachers,
        'class_sections': class_sections,
        'existing_allocations': existing_allocations,
        'current_year': current_year,
    })


@login_required
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    allocations = teacher.allocations.select_related('class_section', 'class_section__grade_level')
    return render(request, 'teachers/teacher_detail.html', {
        'teacher': teacher,
        'allocations': allocations,
    })
