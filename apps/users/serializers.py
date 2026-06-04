"""
User serializers.

RegisterSerializer    — validates & creates a new user account.
LoginSerializer       — validates credentials and returns JWT tokens.
UserProfileSerializer — read/write profile representation.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registration payload.

    password / confirm_password are write-only and not stored directly —
    set_password() is called inside the service layer.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "role",
            "password",
            "confirm_password",
            # Optional profile fields
            "company_name",
            "company_website",
            "university",
            "graduation_year",
        ]
        extra_kwargs = {
            "company_name": {"required": False},
            "company_website": {"required": False},
            "university": {"required": False},
            "graduation_year": {"required": False},
        }

    # ---------------------------------------------------------------- validate
    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def validate_role(self, value: str) -> str:
        allowed = {User.Role.STUDENT, User.Role.COMPANY}
        if value not in allowed:
            raise serializers.ValidationError(
                f"Role must be one of: {', '.join(allowed)}."
            )
        return value

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        role = attrs.get("role")

        if role == User.Role.COMPANY and not attrs.get("company_name"):
            raise serializers.ValidationError(
                {"company_name": "Company name is required for company accounts."}
            )

        if role == User.Role.STUDENT:
            # Clear company-specific fields
            attrs.setdefault("company_name", "")
            attrs.setdefault("company_website", "")

        if role == User.Role.COMPANY:
            # Clear student-specific fields
            attrs.setdefault("university", "")
            attrs.pop("graduation_year", None)

        return attrs

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Authenticates email + password, returns the User instance."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs: dict) -> dict:
        email = attrs["email"].lower()
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid email or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account has been deactivated."}
            )

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Full profile — read-only fields are enforced so a user cannot
    accidentally change their email or role via this endpoint.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "company_name",
            "company_website",
            "university",
            "graduation_year",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "date_joined"]

    def validate(self, attrs: dict) -> dict:
        user = self.instance
        role = user.role if user else attrs.get("role")

        if role == User.Role.COMPANY and "company_name" in attrs:
            if not attrs["company_name"]:
                raise serializers.ValidationError(
                    {"company_name": "Company name cannot be blank."}
                )

        return attrs
