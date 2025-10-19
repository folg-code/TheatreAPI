from django.test import TestCase
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer

User = get_user_model()


class UserSerializerTests(TestCase):

    def test_create_user_serializer_successful(self):
        """Test creating a new user via the serializer is successful"""
        data = {
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])

    def test_password_write_only(self):
        """Test that password is write-only in the serializer"""
        data = {
            "email": "writeonly@example.com",
            "password": "strongpassword",
        }
        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.data

        self.assertNotIn("password", user_data)

    def test_password_min_length(self):
        """Test that serializer enforces minimum password length"""
        data = {
            "email": "shortpass@example.com",
            "password": "123",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)
        self.assertIn("Ensure this field has at least 8 characters", str(serializer.errors["password"]))

    def test_missing_email_raises_error(self):
        """Test that missing email field raises validation error"""
        data = {
            "password": "strongpassword123",
        }
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

