import pytest
from django.test.utils import override_settings
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture(autouse=True)
def use_sqlite(settings):
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_data():
    return {
        "email": "student@example.com",
        "full_name": "Alice Student",
        "role": User.Role.STUDENT,
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "university": "MIT",
        "graduation_year": 2027,
    }


@pytest.fixture
def company_data():
    return {
        "email": "company@example.com",
        "full_name": "Bob Corp",
        "role": User.Role.COMPANY,
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "company_name": "Tech Corp",
        "company_website": "https://techcorp.com",
    }


@pytest.fixture
def student_user(db):
    return User.objects.create_user(
        email="student@example.com",
        password="StrongPass123!",
        full_name="Alice Student",
        role=User.Role.STUDENT,
        university="MIT",
        graduation_year=2027,
    )


@pytest.fixture
def company_user(db):
    return User.objects.create_user(
        email="company@example.com",
        password="StrongPass123!",
        full_name="Bob Corp",
        role=User.Role.COMPANY,
        company_name="Tech Corp",
        company_website="https://techcorp.com",
    )


@pytest.fixture
def other_company_user(db):
    return User.objects.create_user(
        email="othercorp@example.com",
        password="StrongPass123!",
        full_name="Other Corp",
        role=User.Role.COMPANY,
        company_name="Other Corp",
    )


@pytest.fixture
def student_client(student_user):
    client = APIClient()
    client.force_authenticate(user=student_user)
    return client


@pytest.fixture
def company_client(company_user):
    client = APIClient()
    client.force_authenticate(user=company_user)
    return client


@pytest.fixture
def other_company_client(other_company_user):
    client = APIClient()
    client.force_authenticate(user=other_company_user)
    return client
