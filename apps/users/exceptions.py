"""
Custom DRF exception handler.

Normalises all error responses to:
{
    "errors": {
        "field_name": ["message", ...],  -- validation errors
        "detail": "message"              -- non-field / auth errors
    }
}
"""
import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Let DRF build the initial response first.
    response = exception_handler(exc, context)

    if response is None:
        # Unhandled exception — log it and return 500.
        logger.exception("Unhandled exception in view %s", context.get("view"))
        return Response(
            {"errors": {"detail": "An unexpected error occurred. Please try again later."}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Normalise the payload shape.
    if isinstance(response.data, dict):
        if "detail" in response.data:
            response.data = {"errors": {"detail": str(response.data["detail"])}}
        else:
            response.data = {"errors": response.data}
    elif isinstance(response.data, list):
        response.data = {"errors": {"detail": response.data}}

    return response
