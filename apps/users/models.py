"""
Custom User model replacing Django's default.
Adds a `role` field to distinguish student vs company accounts.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager that uses email as the unique identifier."""

    def _create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError("Email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.STUDENT)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Platform user.

    Roles
    -----
    STUDENT  — can browse and apply for internships.
    COMPANY  — can create, update, and delete internships.
    """

    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        COMPANY = "company", "Company"

    # ------------------------------------------------------------------ fields
    email = models.EmailField(unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Company-specific profile fields (null for students)
    company_name = models.CharField(max_length=255, blank=True, default="")
    company_website = models.URLField(blank=True, default="")

    # Student-specific profile fields (null for companies)
    university = models.CharField(max_length=255, blank=True, default="")
    graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)

    # Django internals
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "role"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["role"], name="idx_user_role"),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"

    # ---------------------------------------------------------------- helpers
    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT

    @property
    def is_company(self) -> bool:
        return self.role == self.Role.COMPANY
