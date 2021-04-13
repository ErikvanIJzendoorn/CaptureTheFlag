"""
Capture_the_Flag URL Configuration

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

# Uncomment next two lines to enable admin:
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static, settings


from Capture_the_Flag.Team import views
from Capture_the_Flag.Main.views import index_main

urlpatterns = [# Uncomment the next line to enable the admin:
    path('', index_main, name='index'),
    path('dadmin/', admin.site.urls),
    path('admin/', include('Capture_the_Flag.Admin.urls')),
    path('dashboard/', include('Capture_the_Flag.Team.urls')),    
    path('team/login', views.login, name='login'),
    path('team/teamprofile/<str:team_code>', views.teamProfile, name='Team profiel'),
    path('team/teamprofile/<str:team_code>/edit', views.editTeamProfile, name='bewerken')
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

