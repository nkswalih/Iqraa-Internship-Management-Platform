"""
Internship-specific permissions.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated

from apps.users.permissions import IsCompany


class IsCompanyOwner(IsCompany):
    """
    Object-level: the request user must be the company that created the
    internship (obj.user == request.user).
    """

    message = "You can only modify internships you created."

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.user == request.user
