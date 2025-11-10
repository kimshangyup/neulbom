"""
URL configuration for neulbom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from neulbom.health import health_check
from neulbom.views import landing_page
from authentication.admin import admin_site

urlpatterns = [
    path('', landing_page, name='landing'),
    path('dashboard/', include('dashboard.urls')),
    path('admin/', admin_site.urls),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('authentication.urls')),
    path('instructors/', include('instructors.urls')),
    path('students/', include('students.urls')),
]

# Custom error handlers
handler403 = 'neulbom.views.permission_denied'
