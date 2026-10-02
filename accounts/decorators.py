from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            user_role = getattr(getattr(request, 'user', None), 'profile', None)
            if user_role and user_role.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, 'මෙම පිටුවට ප්‍රවේශ වීමට ඔබට අවසර නොමැත. (Access Denied)')
            return redirect('dashboard')
        return _wrapped_view
    return decorator

def principal_or_admin_required(view_func):
    return role_required(['ADMIN', 'PRINCIPAL'])(view_func)

def teacher_or_staff_required(view_func):
    return role_required(['ADMIN', 'PRINCIPAL', 'TEACHER'])(view_func)
