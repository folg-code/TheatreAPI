from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserViewsTests(APITestCase):

    def setUp(self):
        self.user_data = {
            "email": "testuser@example.com",
            "password": "StrongPass123",
            "first_name": "Test",
            "last_name": "User",
        }
        self.user = User.objects.create_user(**self.user_data)

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def test_register_user(self):
        url = reverse("user:create")
        data = {
            "email": "newuser@example.com",
            "password": "NewStrongPass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=data["email"]).exists())
        self.assertNotIn("password", response.data)

    def test_register_user_missing_password(self):
        url = reverse("user:create")
        data = {"email": "nopass@example.com"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_get_profile_authenticated(self):
        url = reverse("user:manage")
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_profile_unauthenticated(self):
        url = reverse("user:manage")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile_authenticated(self):
        url = reverse("user:manage")
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"first_name": "Updated", "last_name": "Name"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data["first_name"])
        self.assertEqual(self.user.last_name, data["last_name"])

    def test_partial_update_profile_authenticated(self):
        url = reverse("user:manage")
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        data = {"first_name": "Partial"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, data["first_name"])
