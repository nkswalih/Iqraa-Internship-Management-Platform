"""
Authentication views.

POST /api/auth/register/ — create a new account
POST /api/auth/login/    — obtain JWT token pair
GET  /api/auth/profile/  — retrieve authenticated user's profile
PUT  /api/auth/profile/  — update authenticated user's profile
"""
import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer
from .services import get_tokens_for_user

logger = logging.getLogger(__name__)


class RegisterView(APIView):
    """
    POST /api/auth/register/

    Open endpoint — no authentication required.
    Returns 201 with the user profile and a JWT token pair on success.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        profile = UserProfileSerializer(user).data

        logger.info("New user registered: %s (role=%s)", user.email, user.role)

        return Response(
            {
                "user": profile,
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login/

    Open endpoint — returns a JWT token pair on valid credentials.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        tokens = get_tokens_for_user(user)
        profile = UserProfileSerializer(user).data

        logger.info("User logged in: %s", user.email)

        return Response(
            {
                "user": profile,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    GET /api/auth/profile/ — retrieve own profile
    PUT /api/auth/profile/ — partial update own profile
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
