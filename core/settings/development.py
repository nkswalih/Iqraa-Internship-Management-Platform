from .base import *

DEBUG = env.bool("DEBUG", default=True)

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": env.db()
}