from .base import *

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = [
    "igraainternship.com",
    "www.igraainternship.com",
]

DATABASES = {
    "default": env.db()
}

SECURE_SSL_REDIRECT = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True