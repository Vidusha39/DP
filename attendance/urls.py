from django.urls import path
from . import views

urlpatterns = [
    path('attendance/', views.attendance_overview, name='attendance_overview'),
    path('attendance/mark/<int:class_id>/', views.mark_attendance, name='mark_attendance'),
    path('attendance/export/<int:class_id>/', views.export_excel, name='export_excel'),
    path('attendance/print/<int:class_id>/', views.print_roster, name='print_roster'),
]
