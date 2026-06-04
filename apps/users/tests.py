import pytest
from django.urls import reverse
from rest_framework import status

from apps.users.models import User


pytestmark = pytest.mark.django_db


class TestRegisterView:
    url = reverse("users:register")

    def test_register_student_success(self, api_client, student_data):
        response = api_client.post(self.url, student_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert data["user"]["email"] == "student@example.com"
        assert data["user"]["role"] == User.Role.STUDENT
        assert data["user"]["full_name"] == "Alice Student"
        assert "tokens" in data
        assert "access" in data["tokens"]
        assert "refresh" in data["tokens"]

    def test_register_company_success(self, api_client, company_data):
        response = api_client.post(self.url, company_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["role"] == User.Role.COMPANY
        assert response.data["user"]["company_name"] == "Tech Corp"
        assert response.data["user"]["company_website"] == "https://techcorp.com"
        assert response.data["user"]["university"] == ""

    def test_register_duplicate_email(self, api_client, student_data):
        api_client.post(self.url, student_data, format="json")
        response = api_client.post(self.url, student_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data["errors"]

    def test_register_password_mismatch(self, api_client, student_data):
        student_data["confirm_password"] = "DifferentPass123!"
        response = api_client.post(self.url, student_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "confirm_password" in response.data["errors"]

    def test_register_missing_company_name(self, api_client, company_data):
        del company_data["company_name"]
        response = api_client.post(self.url, company_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "company_name" in response.data["errors"]

    def test_register_weak_password(self, api_client, student_data):
        student_data["password"] = "123"
        student_data["confirm_password"] = "123"
        response = api_client.post(self.url, student_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_student_clears_company_fields(self, api_client, student_data):
        student_data["company_name"] = "ShouldBeIgnored"
        response = api_client.post(self.url, student_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["company_name"] == ""

    def test_register_company_clears_student_fields(self, api_client, company_data):
        company_data["university"] = "ShouldBeIgnored"
        company_data["graduation_year"] = 2025
        response = api_client.post(self.url, company_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"]["university"] == ""
        assert response.data["user"]["graduation_year"] is None


class TestLoginView:
    url = reverse("users:login")

    def test_login_success(self, api_client, student_data):
        api_client.post(reverse("users:register"), student_data, format="json")
        response = api_client.post(self.url, {
            "email": student_data["email"],
            "password": student_data["password"],
        }, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert "access" in response.data["tokens"]

    def test_login_invalid_credentials(self, api_client):
        response = api_client.post(self.url, {
            "email": "nonexistent@example.com",
            "password": "wrong",
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "detail" in response.data["errors"]

    def test_login_inactive_user(self, api_client, student_data):
        api_client.post(reverse("users:register"), student_data, format="json")
        User.objects.filter(email=student_data["email"]).update(is_active=False)
        response = api_client.post(self.url, {
            "email": student_data["email"],
            "password": student_data["password"],
        }, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestProfileView:
    url = reverse("users:profile")

    def test_get_profile_authenticated(self, student_client):
        response = student_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "student@example.com"
        assert response.data["role"] == User.Role.STUDENT

    def test_get_profile_unauthenticated(self, api_client):
        response = api_client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, student_client):
        response = student_client.put(self.url, {"full_name": "Alice Updated"}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["full_name"] == "Alice Updated"

    def test_update_profile_read_only_fields(self, student_client):
        response = student_client.put(self.url, {
            "email": "hacked@example.com",
            "role": User.Role.COMPANY,
        }, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "student@example.com"
        assert response.data["role"] == User.Role.STUDENT

    def test_update_profile_company_name_required_for_company(self, company_client):
        response = company_client.put(self.url, {"company_name": ""}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
