"""
Application model.

A student submits one Application per Internship.
Duplicate prevention is enforced at both the ORM level (UniqueConstraint)
and the database level (the constraint generates a UNIQUE INDEX in Postgres).
"""
from django.conf import settings
from django.db import models


class Application(models.Model):
    """
    Tracks a student's application to a specific internship.

    Constraints
    -----------
    * A student can apply to the same internship only once.
      Enforced by UniqueConstraint(fields=["user", "internship"]).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWING = "reviewing", "Reviewing"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    # ---------------------------------------------------------------- relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
        db_index=True,
        help_text="The student who applied.",
    )
    internship = models.ForeignKey(
        "internships.Internship",
        on_delete=models.CASCADE,
        related_name="applications",
        db_index=True,
    )

    # ---------------------------------------------------------------- content
    cover_letter = models.TextField(
        blank=True,
        default="",
        help_text="Optional cover letter from the student.",
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    # --------------------------------------------------------------- timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "applications"
        ordering = ["-applied_at"]
        constraints = [
            # DATABASE-LEVEL guarantee: one application per (student, internship).
            models.UniqueConstraint(
                fields=["user", "internship"],
                name="uq_application_user_internship",
            )
        ]
        indexes = [
            models.Index(fields=["user", "status"], name="idx_application_user_status"),
            models.Index(
                fields=["internship", "status"],
                name="idx_app_internship_status",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.user.email} → {self.internship.title} [{self.status}]"
        )
