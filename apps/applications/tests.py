import pytest
from django.urls import reverse
from rest_framework import status

from apps.applications.models import Application
from apps.internships.models import Internship


pytestmark = pytest.mark.django_db


class TestApplicationListCreateView:
    list_url = reverse("applications:list-create")

    def _create_open_internship(self, user):
        return Internship.objects.create(
            user=user,
            title="Software Engineering Intern",
            description="Build cool stuff",
            location="San Francisco, CA",
            duration_weeks=12,
            status=Internship.Status.OPEN,
        )

    def _create_closed_internship(self, user):
        return Internship.objects.create(
            user=user,
            title="Closed Internship",
            description="N/A",
            location="Remote",
            duration_weeks=6,
            status=Internship.Status.CLOSED,
        )

    # --- POST: create application ---

    def test_apply_as_student_success(self, student_client, student_user, company_user):
        internship = self._create_open_internship(company_user)
        response = student_client.post(self.list_url, {
            "internship_id": internship.pk,
            "cover_letter": "I love this role!",
        }, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["applicant"]["email"] == "student@example.com"
        assert response.data["status"] == Application.Status.PENDING
        assert response.data["internship"]["title"] == "Software Engineering Intern"

    def test_apply_as_company_forbidden(self, company_client, company_user):
        internship = self._create_open_internship(company_user)
        response = company_client.post(self.list_url, {
            "internship_id": internship.pk,
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_apply_unauthenticated(self, api_client, company_user):
        internship = self._create_open_internship(company_user)
        response = api_client.post(self.list_url, {
            "internship_id": internship.pk,
        }, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_apply_to_own_internship_forbidden(self, company_client, company_user):
        internship = self._create_open_internship(company_user)
        response = company_client.post(self.list_url, {
            "internship_id": internship.pk,
        }, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_apply_duplicate_application(self, student_client, student_user, company_user):
        internship = self._create_open_internship(company_user)
        student_client.post(self.list_url, {"internship_id": internship.pk}, format="json")
        response = student_client.post(self.list_url, {"internship_id": internship.pk}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already applied" in str(response.data["errors"]["internship_id"]).lower()

    def test_apply_to_nonexistent_internship(self, student_client):
        response = student_client.post(self.list_url, {"internship_id": 99999}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_apply_to_closed_internship(self, student_client, student_user, company_user):
        internship = self._create_closed_internship(company_user)
        response = student_client.post(self.list_url, {"internship_id": internship.pk}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    # --- GET: list applications ---

    def test_list_applications_as_student_sees_own(self, student_client, student_user, company_user):
        internship = self._create_open_internship(company_user)
        Application.objects.create(user=student_user, internship=internship)
        response = student_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["applicant"]["email"] == student_user.email

    def test_list_applications_as_company_sees_own_internships(self, company_client, company_user, student_user):
        internship = self._create_open_internship(company_user)
        Application.objects.create(user=student_user, internship=internship)
        response = company_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["internship"]["title"] == "Software Engineering Intern"

    def test_list_applications_as_company_does_not_see_others(self, company_client, company_user, other_company_user, student_user):
        internship = self._create_open_internship(other_company_user)
        Application.objects.create(user=student_user, internship=internship)
        response = company_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_applications_unauthenticated(self, api_client):
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
