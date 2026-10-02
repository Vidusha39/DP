def user_role_context(request):
    """
    Makes role checks readily available in all Django templates.
    """
    if not request.user.is_authenticated:
        return {
            'user_role': None,
            'is_admin': False,
            'is_principal': False,
            'is_teacher': False,
            'is_staff_or_admin': False,
        }
    
    role = 'TEACHER'
    if request.user.is_superuser:
        role = 'ADMIN'
    elif hasattr(request.user, 'profile'):
        role = request.user.profile.role

    is_admin = role == 'ADMIN' or request.user.is_superuser
    is_principal = role == 'PRINCIPAL'
    is_teacher = role == 'TEACHER'
    is_staff_or_admin = is_admin or is_principal

    return {
        'user_role': role,
        'is_admin': is_admin,
        'is_principal': is_principal,
        'is_teacher': is_teacher,
        'is_staff_or_admin': is_staff_or_admin,
    }
