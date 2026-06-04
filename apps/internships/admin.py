"""
Admin configuration for the internships app.
"""
from django.contrib import admin

from .models import Internship


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "get_company",
        "location",
        "is_remote",
        "status",
        "duration_weeks",
        "application_deadline",
        "created_at",
    )
    list_filter = ("status", "is_remote", "created_at")
    search_fields = ("title", "description", "user__email", "user__company_name")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("user",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    @admin.display(description="Company", ordering="user__company_name")
    def get_company(self, obj):
        return obj.user.company_name or obj.user.email
