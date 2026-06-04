from .base import *

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": env.db()
}