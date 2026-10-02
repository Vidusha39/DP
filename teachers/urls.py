from django.urls import path
from . import views

urlpatterns = [
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/add/', views.create_teacher, name='create_teacher'),
    path('teachers/allocate/', views.allocate_teacher, name='allocate_teacher'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:teacher_id>/edit/', views.edit_teacher, name='edit_teacher'),
    path('teachers/<int:teacher_id>/delete/', views.delete_teacher, name='delete_teacher'),
    path('teachers/<int:teacher_id>/toggle-status/', views.toggle_teacher_status, name='toggle_teacher_status'),
]
