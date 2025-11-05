from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


User = get_user_model()


@extend_schema(
    tags=["User"],
    summary="Register a new user",
    description="Create a new user account. No authentication required.",
    request=UserSerializer,
    responses={201: UserSerializer},
    examples=[
        OpenApiExample(
            "Example Request",
            value={
                "email": "newuser@example.com",
                "password": "StrongPassword123",
                "first_name": "John",
                "last_name": "Doe",
            },
        ),
        OpenApiExample(
            "Example Response",
            value={
                "id": 1,
                "email": "newuser@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            response_only=True,
        ),
    ],
)
class CreateUserView(generics.CreateAPIView):
    """
    POST /api/user/register/

    Public endpoint for user registration.
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


@extend_schema(
    tags=["User"],
    summary="Retrieve or update the current user profile",
    description="Get or update the authenticated user's profile. Requires a valid JWT token.",
    request=UserSerializer,
    responses={
        200: UserSerializer,
        401: OpenApiExample(
            "Unauthorized",
            value={"detail": "Authentication credentials were not provided."},
        ),
    },
    examples=[
        OpenApiExample(
            "Example Response",
            value={
                "id": 1,
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
            },
            response_only=True,
        ),
        OpenApiExample(
            "Example Update Request",
            value={
                "first_name": "Updated",
                "last_name": "User",
            },
            request_only=True,
        ),
    ],
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    GET, PUT, PATCH /api/user/me/

    Endpoint for authenticated users to view or update their profile.
    """
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Return the currently authenticated user."""
        return self.request.user
