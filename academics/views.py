from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max
from datetime import date

from .models import GradeLevel, Classroom, ClassSection, AcademicYear
from .forms import GradeLevelForm, ClassroomForm, GradeLocationAllocationForm
from accounts.decorators import principal_or_admin_required
from students.models import Student
from teachers.models import TeacherAllocation


def get_current_academic_year():
    """Returns the current academic year or creates one for the current year."""
    year_obj = AcademicYear.objects.filter(is_current=True).first()
    if not year_obj:
        current_calendar_year = date.today().year
        year_obj, _ = AcademicYear.objects.get_or_create(
            year=current_calendar_year,
            defaults={'is_current': True}
        )
    return year_obj


@login_required
@principal_or_admin_required
def grade_list(request):
    """
    Displays all grades with their order index, allocated locations (classrooms),
    active student counts, and class teachers.
    Available to Admin and Principal only.
    """
    current_year = get_current_academic_year()
    grades = GradeLevel.objects.all().order_by('order_index')
    
    grade_summaries = []
    for g in grades:
        section = ClassSection.objects.filter(
            grade_level=g, 
            academic_year=current_year
        ).select_related('classroom').first()

        classroom = section.classroom if section else None
        
        # Enrolled student count for this grade in the current year
        student_count = Student.objects.filter(
            assigned_class__grade_level=g,
            assigned_class__academic_year=current_year,
            status='APPROVED'
        ).count()

        # If assigned_class was not set yet, fallback to applied_grade approved count
        if student_count == 0:
            student_count = Student.objects.filter(
                applied_grade=g,
                status='APPROVED'
            ).count()

        pending_count = Student.objects.filter(
            applied_grade=g,
            status='PENDING'
        ).count()

        # Class teacher allocation
        class_teacher = None
        if section:
            teacher_alloc = TeacherAllocation.objects.filter(
                class_section=section, 
                is_class_teacher=True
            ).select_related('teacher').first()
            if teacher_alloc:
                class_teacher = teacher_alloc.teacher

        grade_summaries.append({
            'grade': g,
            'section': section,
            'classroom': classroom,
            'student_count': student_count,
            'pending_count': pending_count,
            'class_teacher': class_teacher,
        })

    classrooms_count = Classroom.objects.count()

    return render(request, 'academics/grade_list.html', {
        'grade_summaries': grade_summaries,
        'current_year': current_year,
        'total_grades': grades.count(),
        'total_classrooms': classrooms_count,
    })


@login_required
@principal_or_admin_required
def grade_create(request):
    """
    Create a new GradeLevel and optionally allocate an initial classroom/location.
    Available to Admin and Principal only.
    """
    current_year = get_current_academic_year()

    if request.method == 'POST':
        form = GradeLevelForm(request.POST)
        if form.is_valid():
            grade = form.save()
            chosen_classroom = form.cleaned_data.get('classroom')

            # Ensure a ClassSection exists for the current academic year
            section, _ = ClassSection.objects.get_or_create(
                grade_level=grade,
                academic_year=current_year,
                section_name='ප්‍රධාන',
                defaults={'classroom': chosen_classroom}
            )
            if chosen_classroom and section.classroom != chosen_classroom:
                section.classroom = chosen_classroom
                section.save()

            messages.success(request, f'"{grade.name}" සාර්ථකව නව ශ්‍රේණියක් ලෙස පද්ධතියට එක් කරන ලදී.')
            return redirect('grade_list')
        else:
            messages.error(request, 'කරුණාකර පෝරමයේ ඇති දෝෂ නිවැරදි කරන්න.')
    else:
        # Pre-fill next order index
        max_order = GradeLevel.objects.aggregate(Max('order_index'))['order_index__max'] or 0
        form = GradeLevelForm(initial={'order_index': max_order + 1})

    return render(request, 'academics/grade_form.html', {
        'form': form,
        'is_edit': False,
        'current_year': current_year,
    })


@login_required
@principal_or_admin_required
def grade_edit(request, grade_id):
    """
    Edit an existing GradeLevel and its allocated location.
    Available to Admin and Principal only.
    """
    grade = get_object_or_404(GradeLevel, id=grade_id)
    current_year = get_current_academic_year()
    section = ClassSection.objects.filter(
        grade_level=grade, 
        academic_year=current_year
    ).first()

    if request.method == 'POST':
        form = GradeLevelForm(request.POST, instance=grade, current_section=section)
        if form.is_valid():
            grade = form.save()
            chosen_classroom = form.cleaned_data.get('classroom')

            if section:
                section.classroom = chosen_classroom
                section.save()
            else:
                ClassSection.objects.create(
                    grade_level=grade,
                    academic_year=current_year,
                    section_name='ප්‍රධාන',
                    classroom=chosen_classroom
                )

            messages.success(request, f'"{grade.name}" ශ්‍රේණියේ තොරතුරු සාර්ථකව යාවත්කාලීන කරන ලදී.')
            return redirect('grade_list')
        else:
            messages.error(request, 'කරුණාකර පෝරමයේ ඇති දෝෂ නිවැරදි කරන්න.')
    else:
        form = GradeLevelForm(instance=grade, current_section=section)

    return render(request, 'academics/grade_form.html', {
        'form': form,
        'grade': grade,
        'is_edit': True,
        'current_year': current_year,
    })


@login_required
@principal_or_admin_required
def grade_delete(request, grade_id):
    """
    Delete a GradeLevel with safety checks against deleting grades that have enrolled students.
    Available to Admin and Principal only.
    """
    grade = get_object_or_404(GradeLevel, id=grade_id)
    
    # Students who applied to this grade or are assigned to it
    applied_count = grade.applied_students.count()
    assigned_count = Student.objects.filter(assigned_class__grade_level=grade).count()
    total_students = applied_count + assigned_count

    if total_students > 0:
        if request.method == 'POST':
            messages.error(
                request,
                f'"{grade.name}" ශ්‍රේණිය මකා දැමිය නොහැක! මෙම ශ්‍රේණියට ලියාපදිංචි වී හෝ අයදුම් කර ඇති සිසුන් {total_students} දෙනෙකු පද්ධතියේ සිටී. කරුණාකර පළමුව එම සිසුන්ගේ ශ්‍රේණිය වෙනස් කරන්න හෝ ඉවත් කරන්න.'
            )
            return redirect('grade_list')
        return render(request, 'academics/grade_confirm_delete.html', {
            'grade': grade,
            'cannot_delete': True,
            'total_students': total_students,
            'applied_count': applied_count,
            'assigned_count': assigned_count,
        })

    if request.method == 'POST':
        grade_name = grade.name
        grade.delete()
        messages.success(request, f'"{grade_name}" ශ්‍රේණිය සාර්ථකව පද්ධතියෙන් මකා දමන ලදී.')
        return redirect('grade_list')

    return render(request, 'academics/grade_confirm_delete.html', {
        'grade': grade,
        'cannot_delete': False,
    })


@login_required
@principal_or_admin_required
def allocate_grade_location(request):
    """
    Allocate or change locations (classrooms/halls) for grades in the current academic year.
    Supports single allocation or batch updates.
    Available to Admin and Principal only.
    """
    current_year = get_current_academic_year()
    grades = GradeLevel.objects.all().order_by('order_index')
    classrooms = Classroom.objects.all().order_by('name')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'single_allocation':
            grade_id = request.POST.get('grade_id')
            classroom_id = request.POST.get('classroom_id')

            if grade_id:
                grade = get_object_or_404(GradeLevel, id=grade_id)
                classroom = Classroom.objects.filter(id=classroom_id).first() if classroom_id else None

                section, _ = ClassSection.objects.get_or_create(
                    grade_level=grade,
                    academic_year=current_year,
                    section_name='ප්‍රධාන',
                )
                section.classroom = classroom
                section.save()

                loc_name = classroom.name if classroom else "ස්ථානයක් වෙන් කර නැත"
                messages.success(request, f'"{grade.name}" ශ්‍රේණිය සඳහා ස්ථානය ලෙස "{loc_name}" සාර්ථකව අනුයුක්ත කරන ලදී.')
                return redirect('allocate_grade_location')

        elif action == 'batch_allocation':
            updated_count = 0
            for g in grades:
                field_key = f'classroom_for_grade_{g.id}'
                if field_key in request.POST:
                    room_id = request.POST.get(field_key)
                    room = Classroom.objects.filter(id=room_id).first() if room_id else None

                    section, _ = ClassSection.objects.get_or_create(
                        grade_level=g,
                        academic_year=current_year,
                        section_name='ප්‍රධාන',
                    )
                    if section.classroom != room:
                        section.classroom = room
                        section.save()
                        updated_count += 1

            messages.success(request, f'ශ්‍රේණි සඳහා ස්ථාන අනුයුක්ත කිරීම් සාර්ථකව සුරකින ලදී. (වෙනස්කම්: {updated_count})')
            return redirect('allocate_grade_location')

    # Prepare grades overview with current allocation and student numbers
    allocation_list = []
    for g in grades:
        section = ClassSection.objects.filter(
            grade_level=g,
            academic_year=current_year
        ).select_related('classroom').first()

        classroom = section.classroom if section else None

        student_count = Student.objects.filter(
            assigned_class__grade_level=g,
            assigned_class__academic_year=current_year,
            status='APPROVED'
        ).count()
        if student_count == 0:
            student_count = Student.objects.filter(
                applied_grade=g,
                status='APPROVED'
            ).count()

        is_over_capacity = False
        if classroom and student_count > classroom.capacity:
            is_over_capacity = True

        allocation_list.append({
            'grade': g,
            'section': section,
            'classroom': classroom,
            'student_count': student_count,
            'is_over_capacity': is_over_capacity,
        })

    allocation_form = GradeLocationAllocationForm()
    classroom_form = ClassroomForm()

    return render(request, 'academics/allocate_location.html', {
        'allocation_list': allocation_list,
        'classrooms': classrooms,
        'current_year': current_year,
        'allocation_form': allocation_form,
        'classroom_form': classroom_form,
    })


@login_required
@principal_or_admin_required
def create_classroom(request):
    """
    Create a new Classroom / Hall location.
    Available to Admin and Principal only.
    """
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            messages.success(request, f'"{classroom.name}" (ධාරිතාව: {classroom.capacity}) නව ස්ථානය සාර්ථකව එක් කරන ලදී.')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('allocate_grade_location')


@login_required
@principal_or_admin_required
def delete_classroom(request, classroom_id):
    """
    Delete an unused Classroom / Hall location.
    Available to Admin and Principal only.
    """
    classroom = get_object_or_404(Classroom, id=classroom_id)
    current_year = get_current_academic_year()

    # Check if currently assigned to any sections
    assigned_sections = ClassSection.objects.filter(
        classroom=classroom,
        academic_year=current_year
    ).select_related('grade_level')

    if assigned_sections.exists():
        grades_str = ", ".join([s.grade_level.name for s in assigned_sections])
        messages.error(
            request, 
            f'"{classroom.name}" ස්ථානය මකා දැමිය නොහැක! එය දැනටමත් ({grades_str}) ශ්‍රේණි සඳහා වෙන් කර ඇත. කරුණාකර පළමුව එම ශ්‍රේණිවල ස්ථාන වෙනස් කරන්න.'
        )
    else:
        name = classroom.name
        classroom.delete()
        messages.success(request, f'"{name}" ස්ථානය සාර්ථකව පද්ධතියෙන් මකා දමන ලදී.')

    return redirect('allocate_grade_location')
