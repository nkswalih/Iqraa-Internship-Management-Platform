"""
Internship serializers.

InternshipReadSerializer  — detailed output (includes company info).
InternshipWriteSerializer — validated input for create / update.
"""
from rest_framework import serializers

from .models import Internship


class CompanyBriefSerializer(serializers.Serializer):
    """Minimal company info nested inside internship responses."""

    id = serializers.IntegerField()
    full_name = serializers.CharField()
    company_name = serializers.CharField()
    company_website = serializers.URLField()


class InternshipReadSerializer(serializers.ModelSerializer):
    """Full internship detail, including nested company snapshot."""

    company = CompanyBriefSerializer(source="user", read_only=True)
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = [
            "id",
            "title",
            "description",
            "location",
            "is_remote",
            "stipend",
            "skills_required",
            "duration_weeks",
            "application_deadline",
            "status",
            "company",
            "application_count",
            "created_at",
            "updated_at",
        ]

    def get_application_count(self, obj: Internship) -> int:
        # Applications are prefetched by the view.
        if hasattr(obj, "_prefetched_objects_cache") and "applications" in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache["applications"])
        return obj.applications.count()


class InternshipWriteSerializer(serializers.ModelSerializer):
    """
    Validates internship create / update payloads.

    `user` is injected by the view — not accepted from the client.
    """

    class Meta:
        model = Internship
        fields = [
            "title",
            "description",
            "location",
            "is_remote",
            "stipend",
            "skills_required",
            "duration_weeks",
            "application_deadline",
            "status",
        ]

    def validate_duration_weeks(self, value: int) -> int:
        if value < 1:
            raise serializers.ValidationError("Duration must be at least 1 week.")
        if value > 104:
            raise serializers.ValidationError("Duration cannot exceed 104 weeks (2 years).")
        return value

    def validate_stipend(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("Stipend cannot be negative.")
        return value

    def create(self, validated_data: dict) -> Internship:
        return Internship.objects.create(**validated_data)

    def update(self, instance: Internship, validated_data: dict) -> Internship:
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
