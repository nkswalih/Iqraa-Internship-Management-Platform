"""
Application views.

POST /api/applications/ — student submits an application
GET  /api/applications/ — list applications
    - students see their own applications
    - companies see applications for their internships
"""
import logging

from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsStudent

from .models import Application
from .serializers import ApplicationReadSerializer, ApplicationWriteSerializer

logger = logging.getLogger(__name__)


class ApplicationListCreateView(APIView):
    """
    GET  — scoped list (student → own apps; company → apps on their postings)
    POST — submit new application (student only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStudent()]
        return [IsAuthenticated()]

    # ------------------------------------------------------------------ GET
    def get(self, request):
        user = request.user

        if user.is_student:
            qs = (
                Application.objects
                .filter(user=user)
                .select_related(
                    "internship",
                    "internship__user",
                )
                .prefetch_related("internship__applications")
            )
        else:
            # Company: applications for all their internships.
            qs = (
                Application.objects
                .filter(internship__user=user)
                .select_related(
                    "user",
                    "internship",
                    "internship__user",
                )
                .prefetch_related("internship__applications")
            )

        serializer = ApplicationReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ----------------------------------------------------------------- POST
    def post(self, request):
        serializer = ApplicationWriteSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        try:
            application = serializer.save(user=request.user)
        except IntegrityError:
            # Race condition: another request slipped past the serializer check.
            # The DB UniqueConstraint catches it here.
            return Response(
                {"errors": {"internship_id": "You have already applied for this internship."}},
                status=status.HTTP_409_CONFLICT,
            )

        logger.info(
            "Application submitted: id=%s student=%s internship=%s",
            application.pk,
            request.user.email,
            application.internship_id,
        )

        # Re-fetch with relations for the response.
        application.refresh_from_db()
        application_with_relations = (
            Application.objects
            .select_related("user", "internship", "internship__user")
            .get(pk=application.pk)
        )

        return Response(
            ApplicationReadSerializer(application_with_relations).data,
            status=status.HTTP_201_CREATED,
        )
