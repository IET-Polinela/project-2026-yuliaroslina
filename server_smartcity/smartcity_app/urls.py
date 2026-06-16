"""
URL configuration for npm24782065_iet_2026 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import: from my_app import views
    2. Add a URL to urlpatterns: path('', views.home, name='home')
Class-based views
    1. Add an import: from other_app.views import Home
    2. Add a URL to urlpatterns: path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""

"""
URL configuration for npm24782065_iet_2026 project.
"""

from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from usermanagement_24782065.api_views import RegisterView
from usermanagement_24782065.views import (
    CustomLoginView,
    CustomLogoutView
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Halaman utama dan app
    path('', include('main_app.urls')),
    path('about/', include('about.urls')),
    path('contacts/', include('contacts.urls')),
    path('', include('usermanagement_24782065.urls')),
    path('dashboard/', include('dashboard_24782065.urls')),

    # API Report
    path('api/', include('main_app.api_urls')),

    # JWT Authentication
    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),
    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    # Register Citizen
    path(
        'api/register/',
        RegisterView.as_view(),
        name='api_register'
    ),

    # Login dan logout biasa
    path('login/', CustomLoginView.as_view(), name='login'),
    path(
        'logout/',
        CustomLogoutView.as_view(next_page='login'),
        name='logout'
    ),
]