"""
Internship views.

POST   /api/internships/       — create (company only)
GET    /api/internships/       — list all open internships (any authenticated user)
GET    /api/internships/{id}/  — retrieve detail
PUT    /api/internships/{id}/  — update (owner company only)
DELETE /api/internships/{id}/  — delete (owner company only)
"""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsCompany

from .models import Internship
from .permissions import IsCompanyOwner
from .serializers import InternshipReadSerializer, InternshipWriteSerializer

logger = logging.getLogger(__name__)


class InternshipListCreateView(APIView):
    """
    GET  — list internships (authenticated, any role)
    POST — create internship (company only)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsCompany()]
        return [IsAuthenticated()]

    # ------------------------------------------------------------------  GET
    def get(self, request):
        """
        Returns all OPEN internships, ordered by newest first.
        Company users see their own drafts/closed postings too.
        """
        qs = (
            Internship.objects
            .select_related("user")
            .prefetch_related("applications")
        )

        if not request.user.is_company:
            # Students see only open postings.
            qs = qs.filter(status=Internship.Status.OPEN)

        serializer = InternshipReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ----------------------------------------------------------------- POST
    def post(self, request):
        serializer = InternshipWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        internship = serializer.save(user=request.user)

        logger.info(
            "Internship created: id=%s title=%r by company=%s",
            internship.pk,
            internship.title,
            request.user.email,
        )

        return Response(
            InternshipReadSerializer(internship).data,
            status=status.HTTP_201_CREATED,
        )


class InternshipDetailView(APIView):
    """
    GET    — retrieve one internship (authenticated, any role)
    PUT    — update (owner company only)
    DELETE — delete (owner company only)
    """

    def get_permissions(self):
        if self.request.method in ("PUT", "DELETE"):
            return [IsCompanyOwner()]
        return [IsAuthenticated()]

    def _get_internship(self, pk: int) -> Internship:
        return get_object_or_404(
            Internship.objects.select_related("user").prefetch_related("applications"),
            pk=pk,
        )

    # ------------------------------------------------------------------ GET
    def get(self, request, pk: int):
        internship = self._get_internship(pk)
        serializer = InternshipReadSerializer(internship)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------ PUT
    def put(self, request, pk: int):
        internship = self._get_internship(pk)
        self.check_object_permissions(request, internship)

        serializer = InternshipWriteSerializer(
            internship,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(
            InternshipReadSerializer(updated).data,
            status=status.HTTP_200_OK,
        )

    # ---------------------------------------------------------------- DELETE
    def delete(self, request, pk: int):
        internship = self._get_internship(pk)
        self.check_object_permissions(request, internship)
        internship.delete()

        logger.info(
            "Internship deleted: id=%s by company=%s",
            pk,
            request.user.email,
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
