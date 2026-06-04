"""
Internship model.

Only company users can create internships; each internship is owned by
exactly one company account.
"""
from django.conf import settings
from django.db import models


class Internship(models.Model):
    """A job internship posting created by a company."""

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        DRAFT = "draft", "Draft"

    # ------------------------------------------------------------------ owner
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="internships",
        db_index=True,
        help_text="The company account that owns this posting.",
    )

    # ----------------------------------------------------------------- content
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)

    stipend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monthly stipend in USD. Leave blank if unpaid.",
    )

    skills_required = models.TextField(
        blank=True,
        default="",
        help_text="Comma-separated list of required skills.",
    )

    duration_weeks = models.PositiveSmallIntegerField(
        help_text="Expected duration of the internship in weeks."
    )

    application_deadline = models.DateField(
        null=True,
        blank=True,
        help_text="Last date to apply. Null means no deadline.",
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )

    # --------------------------------------------------------------- timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "internships"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"], name="idx_internship_status_date"),
            models.Index(fields=["user", "status"], name="idx_internship_user_status"),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.user.company_name or self.user.email}"
