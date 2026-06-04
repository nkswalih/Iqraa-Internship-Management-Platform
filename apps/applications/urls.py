"""
URL patterns for the applications app.
Mounted at: /api/applications/
"""
from django.urls import path

from .views import ApplicationListCreateView

app_name = "applications"

urlpatterns = [
    path("", ApplicationListCreateView.as_view(), name="list-create"),
]
