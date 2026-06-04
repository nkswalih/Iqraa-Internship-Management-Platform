"""
Root URL configuration.
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth endpoints: /api/auth/register/, /api/auth/login/, /api/auth/profile/
    path("api/auth/", include("apps.users.urls", namespace="users")),

    # Internship endpoints: /api/internships/
    path("api/internships/", include("apps.internships.urls", namespace="internships")),

    # Application endpoints: /api/applications/
    path("api/applications/", include("apps.applications.urls", namespace="applications")),
]
