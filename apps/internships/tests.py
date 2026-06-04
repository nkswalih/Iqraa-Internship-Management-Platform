import pytest
from django.urls import reverse
from rest_framework import status

from apps.internships.models import Internship


pytestmark = pytest.mark.django_db


def _internship_data(**overrides):
    data = {
        "title": "Software Engineering Intern",
        "description": "Build cool stuff",
        "location": "San Francisco, CA",
        "is_remote": True,
        "stipend": 5000.00,
        "skills_required": "Python, Django, REST",
        "duration_weeks": 12,
        "application_deadline": "2027-06-01",
        "status": Internship.Status.OPEN,
    }
    data.update(overrides)
    return data


class TestInternshipListCreateView:
    list_url = reverse("internships:list-create")

    def test_create_internship_as_company(self, company_client):
        response = company_client.post(self.list_url, _internship_data(), format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Software Engineering Intern"
        assert response.data["company"]["company_name"] == "Tech Corp"

    def test_create_internship_as_student_forbidden(self, student_client):
        response = student_client.post(self.list_url, _internship_data(), format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_internship_unauthenticated(self, api_client):
        response = api_client.post(self.list_url, _internship_data(), format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_internship_invalid_duration(self, company_client):
        response = company_client.post(self.list_url, _internship_data(duration_weeks=0), format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_internship_negative_stipend(self, company_client):
        response = company_client.post(self.list_url, _internship_data(stipend=-100), format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_internship_excessive_duration(self, company_client):
        response = company_client.post(self.list_url, _internship_data(duration_weeks=200), format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_internships_as_student_sees_only_open(self, student_client, company_user):
        open_internship = Internship.objects.create(
            user=company_user, title="Open Internship", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.OPEN,
        )
        Internship.objects.create(
            user=company_user, title="Draft Internship", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.DRAFT,
        )
        Internship.objects.create(
            user=company_user, title="Closed Internship", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.CLOSED,
        )
        response = student_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        titles = [item["title"] for item in response.data]
        assert "Open Internship" in titles
        assert "Draft Internship" not in titles
        assert "Closed Internship" not in titles

    def test_list_internships_as_company_sees_all_own(self, company_client, company_user):
        Internship.objects.create(
            user=company_user, title="My Open", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.OPEN,
        )
        Internship.objects.create(
            user=company_user, title="My Draft", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.DRAFT,
        )
        response = company_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        titles = [item["title"] for item in response.data]
        assert "My Open" in titles
        assert "My Draft" in titles

    def test_list_internships_unauthenticated(self, api_client):
        response = api_client.get(self.list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_has_application_count(self, student_client, company_user):
        internship = Internship.objects.create(
            user=company_user, title="Test", description="desc",
            location="Loc", duration_weeks=10, status=Internship.Status.OPEN,
        )
        response = student_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert "application_count" in response.data[0]


class TestInternshipDetailView:
    def _create_internship(self, user, **kwargs):
        data = dict(title="Test Internship", description="desc", location="Loc",
                    duration_weeks=10, status=Internship.Status.OPEN, **kwargs)
        return Internship.objects.create(user=user, **data)

    def test_get_internship(self, student_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = student_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Internship"

    def test_get_internship_not_found(self, student_client):
        url = reverse("internships:detail", args=[99999])
        response = student_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_internship_as_owner(self, company_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = company_client.put(url, {"title": "Updated Title"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Title"

    def test_update_internship_as_non_owner_forbidden(self, other_company_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = other_company_client.put(url, {"title": "Hacked"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_internship_as_student_forbidden(self, student_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = student_client.put(url, {"title": "Hacked"}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_internship_as_owner(self, company_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = company_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Internship.objects.count() == 0

    def test_delete_internship_as_non_owner_forbidden(self, other_company_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = other_company_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_internship_unauthenticated(self, api_client, company_user):
        internship = self._create_internship(company_user)
        url = reverse("internships:detail", args=[internship.pk])
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
