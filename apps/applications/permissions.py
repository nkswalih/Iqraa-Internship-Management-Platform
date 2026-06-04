"""
Application-specific permission classes.
"""
from rest_framework.permissions import IsAuthenticated


class CanViewApplication(IsAuthenticated):
    """
    Object-level: the user can view the application if they are:
    - the student who submitted it, OR
    - the company that owns the linked internship.
    """

    message = "You do not have permission to view this application."

    def has_object_permission(self, request, view, obj) -> bool:
        return (
            obj.user == request.user
            or obj.internship.user == request.user
        )
