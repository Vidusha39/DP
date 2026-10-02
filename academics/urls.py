from django.urls import path
from . import views

urlpatterns = [
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/add/', views.grade_create, name='grade_create'),
    path('grades/<int:grade_id>/edit/', views.grade_edit, name='grade_edit'),
    path('grades/<int:grade_id>/delete/', views.grade_delete, name='grade_delete'),
    path('grades/locations/', views.allocate_grade_location, name='allocate_grade_location'),
    path('grades/locations/classroom/add/', views.create_classroom, name='create_classroom'),
    path('grades/locations/classroom/<int:classroom_id>/delete/', views.delete_classroom, name='delete_classroom'),
]
