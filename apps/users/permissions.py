"""
Reusable role-based permission classes.

IsStudent  — allows only authenticated students.
IsCompany  — allows only authenticated company users.
IsOwner    — allows only the object owner (object must have a `user` FK).
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsStudent(IsAuthenticated):
    """Request user must be authenticated AND have the student role."""

    message = "Only student accounts can perform this action."

    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view) and request.user.is_student


class IsCompany(IsAuthenticated):
    """Request user must be authenticated AND have the company role."""

    message = "Only company accounts can perform this action."

    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view) and request.user.is_company


class IsOwnerOrReadOnly(IsAuthenticated):
    """
    Object-level permission.

    Safe HTTP methods (GET, HEAD, OPTIONS) are allowed for any authenticated
    user; write operations are restricted to the object owner.

    The object must expose a `.user` attribute pointing to the owning User.
    """

    message = "You do not have permission to modify this resource."

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return obj.user == request.user
