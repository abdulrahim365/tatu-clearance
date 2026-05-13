"""
URL configuration for tatuclearance project.

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

# ✅ CORRECT IMPORTS - Use only the app name 'clearance'
from clearance.views import (
    dashboard, 
    apply_clearance, 
    approve_step, 
    download_certificate
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # TaTu Online Clearance System Routes
    path('', dashboard, name='dashboard'),
    path('apply/', apply_clearance, name='apply_clearance'),
    path('step/<int:step_id>/approve/', approve_step, name='approve_step'),
    path('certificate/<int:request_id>/', download_certificate, name='download_certificate'),
]
