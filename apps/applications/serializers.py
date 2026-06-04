"""
Application serializers.

ApplicationReadSerializer  — detailed output with nested relations.
ApplicationWriteSerializer — validated input for create.
"""
from rest_framework import serializers

from apps.internships.models import Internship
from apps.internships.serializers import InternshipReadSerializer

from .models import Application


class ApplicantBriefSerializer(serializers.Serializer):
    """Minimal student snapshot embedded in application responses."""

    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    university = serializers.CharField()
    graduation_year = serializers.IntegerField()


class ApplicationReadSerializer(serializers.ModelSerializer):
    """
    Full application detail.

    - Students see their own applications with full internship detail.
    - Companies see applications for their internships with applicant detail.
    The view controls which queryset is returned; the serializer just renders it.
    """

    applicant = ApplicantBriefSerializer(source="user", read_only=True)
    internship = InternshipReadSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "internship",
            "applicant",
            "cover_letter",
            "status",
            "applied_at",
            "updated_at",
        ]


class ApplicationWriteSerializer(serializers.ModelSerializer):
    """
    Validates a student's apply request.

    `user` and `internship` are set by the view — not accepted from the client.
    Only `internship_id` and optional `cover_letter` come from the request body.
    """

    internship_id = serializers.PrimaryKeyRelatedField(
        queryset=Internship.objects.filter(status=Internship.Status.OPEN),
        source="internship",
        error_messages={
            "does_not_exist": "Internship not found or is no longer accepting applications.",
            "null": "internship_id is required.",
        },
    )

    class Meta:
        model = Application
        fields = ["internship_id", "cover_letter"]
        extra_kwargs = {
            "cover_letter": {"required": False},
        }

    def validate(self, attrs: dict) -> dict:
        user = self.context["request"].user
        internship = attrs["internship"]

        # Guard: student cannot apply to their own company's internship
        # (edge case — user shouldn't be both student and company, but be safe).
        if internship.user == user:
            raise serializers.ValidationError(
                {"internship_id": "You cannot apply to your own internship."}
            )

        # Guard: duplicate application check at serializer level
        # (the DB constraint is the ultimate enforcement, but we give a clear error here).
        if Application.objects.filter(user=user, internship=internship).exists():
            raise serializers.ValidationError(
                {"internship_id": "You have already applied for this internship."}
            )

        return attrs

    def create(self, validated_data: dict) -> Application:
        return Application.objects.create(**validated_data)
