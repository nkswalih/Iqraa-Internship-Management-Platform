"""
Admin configuration for the applications app.
"""
from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_student_email",
        "get_internship_title",
        "get_company",
        "status",
        "applied_at",
    )
    list_filter = ("status", "applied_at")
    search_fields = (
        "user__email",
        "user__full_name",
        "internship__title",
        "internship__user__company_name",
    )
    readonly_fields = ("applied_at", "updated_at")
    raw_id_fields = ("user", "internship")
    date_hierarchy = "applied_at"
    ordering = ("-applied_at",)

    @admin.display(description="Student", ordering="user__email")
    def get_student_email(self, obj):
        return obj.user.email

    @admin.display(description="Internship", ordering="internship__title")
    def get_internship_title(self, obj):
        return obj.internship.title

    @admin.display(description="Company", ordering="internship__user__company_name")
    def get_company(self, obj):
        return obj.internship.user.company_name or obj.internship.user.email
