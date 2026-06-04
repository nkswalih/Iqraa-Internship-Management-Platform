"""
User service layer.

Keeps view code thin — all business rules live here.
"""
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


def get_tokens_for_user(user: User) -> dict:
    """
    Generate a JWT token pair for *user*.

    Returns
    -------
    {
        "refresh": "<refresh_token>",
        "access":  "<access_token>",
    }
    """
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
