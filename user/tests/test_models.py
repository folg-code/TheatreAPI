from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test that creating a user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = User.objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_new_user_email_normalized(self):
        """Test that the email for a new user is normalized (lowercased domain)"""
        email = "Test@EXAMPLE.COM"
        user = User.objects.create_user(email=email, password="test123")

        self.assertEqual(user.email, "Test@example.com")

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password="test123")

    def test_create_superuser(self):
        """Test creating a superuser"""
        email = "admin@example.com"
        user = User.objects.create_superuser(email=email, password="adminpass123")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_superuser_must_have_is_staff_true(self):
        """Test that creating a superuser without is_staff=True raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_staff=False
            )

    def test_superuser_must_have_is_superuser_true(self):
        """Test that creating a superuser without is_superuser=True raises an error"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="adminpass123",
                is_superuser=False
            )

    def test_str_returns_email(self):
        """Test that the string representation of a user returns the email"""
        email = "user@example.com"
        user = User.objects.create_user(email=email, password="testpass")
        self.assertEqual(str(user), email)
