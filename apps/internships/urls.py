"""
URL patterns for the internships app.
Mounted at: /api/internships/
"""
from django.urls import path

from .views import InternshipDetailView, InternshipListCreateView

app_name = "internships"

urlpatterns = [
    path("", InternshipListCreateView.as_view(), name="list-create"),
    path("<int:pk>/", InternshipDetailView.as_view(), name="detail"),
]
