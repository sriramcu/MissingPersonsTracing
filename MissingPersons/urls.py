"""django_project URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from police import views as police_views
from django.views.generic import RedirectView
from django.conf.urls import re_path, url, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', police_views.register, name='register'),
    path('register_case/', police_views.register_case, name='register_case'),
    path('profile/', police_views.profile, name='profile'),
    path('tables/', police_views.tables, name='tables'),
    path('status/', police_views.status, name='status'),    
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('facial_recognition/', police_views.facial_recognition, name='facial_recognition'),
    path('show_all/', police_views.show_all, name='show_all'),
    path('upload/', police_views.upload, name='upload'),
    path('',police_views.base, name='base'),
    
]
 

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
