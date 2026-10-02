from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.public_register, name='public_register'),
    path('register/success/<int:student_id>/', views.registration_success, name='registration_success'),
    path('students/', views.student_list, name='student_list'),
    path('students/pending/', views.pending_verifications, name='pending_verifications'),
    path('students/verify/<int:student_id>/', views.verify_student, name='verify_student'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
]
