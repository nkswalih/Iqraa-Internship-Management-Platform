# Internship Management Platform — Backend

Django REST Framework API with JWT authentication, role-based access control, and PostgreSQL.

---

## Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.2 + DRF 3.15 |
| Database | PostgreSQL (psycopg2) |
| Auth | SimpleJWT (Bearer tokens) |
| Env config | django-environ |
| Prod server | Gunicorn + WhiteNoise |

---

## Project Structure

```
internship_platform/
├── config/
│   ├── settings/
│   │   ├── base.py          # Shared settings
│   │   ├── dev.py           # Development overrides
│   │   └── prod.py          # Production hardening
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── users/               # Custom user model, JWT auth
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── services.py
│   │   ├── exceptions.py
│   │   └── admin.py
│   ├── internships/         # Internship postings (company-owned)
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   └── admin.py
│   └── applications/        # Student applications
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       ├── urls.py
│       ├── permissions.py
│       └── admin.py
├── requirements.txt
├── manage.py
└── .env.example
```

---

## Quick Start

```bash
# 1. Clone and enter the project
cd internship_platform

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, etc.

# 5. Create PostgreSQL database
createdb internship_db

# 6. Run migrations
python manage.py migrate

# 7. Create a superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

---

## API Reference

All endpoints are prefixed with `/api/`.
Protected endpoints require: `Authorization: Bearer <access_token>`

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register/` | Public | Register student or company account |
| POST | `/api/auth/login/` | Public | Obtain JWT token pair |
| GET | `/api/auth/profile/` | Required | Get own profile |
| PUT | `/api/auth/profile/` | Required | Update own profile |

#### Register — Student
```json
POST /api/auth/register/
{
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "role": "student",
  "password": "Str0ngP@ss!",
  "confirm_password": "Str0ngP@ss!",
  "university": "MIT",
  "graduation_year": 2026
}
```

#### Register — Company
```json
POST /api/auth/register/
{
  "email": "hr@acme.com",
  "full_name": "ACME Recruiter",
  "role": "company",
  "password": "Str0ngP@ss!",
  "confirm_password": "Str0ngP@ss!",
  "company_name": "Acme Corp",
  "company_website": "https://acme.com"
}
```

#### Login
```json
POST /api/auth/login/
{
  "email": "alice@example.com",
  "password": "Str0ngP@ss!"
}
```

Response:
```json
{
  "user": { "id": 1, "email": "...", "role": "student", ... },
  "tokens": {
    "access": "<jwt_access_token>",
    "refresh": "<jwt_refresh_token>"
  }
}
```

---

### Internships

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/api/internships/` | Required | Any | List internships |
| POST | `/api/internships/` | Required | Company | Create internship |
| GET | `/api/internships/{id}/` | Required | Any | Get detail |
| PUT | `/api/internships/{id}/` | Required | Owner company | Update |
| DELETE | `/api/internships/{id}/` | Required | Owner company | Delete |

#### Create Internship
```json
POST /api/internships/
Authorization: Bearer <company_token>

{
  "title": "Backend Engineering Intern",
  "description": "Work on our core API platform...",
  "location": "San Francisco, CA",
  "is_remote": true,
  "stipend": 3000.00,
  "skills_required": "Python, Django, PostgreSQL",
  "duration_weeks": 12,
  "application_deadline": "2026-08-01",
  "status": "open"
}
```

---

### Applications

| Method | Endpoint | Auth | Role | Description |
|--------|----------|------|------|-------------|
| GET | `/api/applications/` | Required | Any | List own applications |
| POST | `/api/applications/` | Required | Student | Apply for internship |

#### Apply
```json
POST /api/applications/
Authorization: Bearer <student_token>

{
  "internship_id": 5,
  "cover_letter": "I'm excited about this opportunity because..."
}
```

---

## Error Format

All errors follow a consistent shape:

```json
{
  "errors": {
    "field_name": ["Error message"],
    "detail": "Non-field error message"
  }
}
```

---

## Key Design Decisions

- **Custom User Model** — email as `USERNAME_FIELD`; role-based with `is_student` / `is_company` properties.
- **APIView-based** — explicit `get_permissions()` per method; no implicit magic from ViewSets.
- **Service layer** (`services.py`) — JWT generation isolated from views.
- **Duplicate application prevention** — dual-layer: serializer-level check (clear error message) + DB `UniqueConstraint` (race condition guard).
- **`select_related` / `prefetch_related`** — used consistently to prevent N+1 queries.
- **Settings split** — `base / dev / prod`; prod enables HSTS, HTTPS redirect, secure cookies.
- **Custom exception handler** — normalises all DRF error responses to `{"errors": {...}}`.

---

## Running in Production

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod \
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```
