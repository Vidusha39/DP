"""
URL configuration for daham_pasala_proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Customize Admin Site Headers in Sinhala
admin.site.site_header = "දහම් පාසල් කළමනාකරණ පද්ධතිය"
admin.site.site_title = "දහම් පාසල"
admin.site.index_title = "පරිපාලන පාලක පුවරුව"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('academics.urls')),
    path('', include('students.urls')),
    path('', include('teachers.urls')),
    path('', include('attendance.urls')),
]

