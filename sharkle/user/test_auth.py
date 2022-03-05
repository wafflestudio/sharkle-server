from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User
from rest_framework import status


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    @classmethod
    def create(cls, **kwargs):
        user = User.objects.create_user(**kwargs)
        return user


# Create your tests here.
class PostSignUpTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            email="signup@sharkle.com",
            user_id="signup",
            username="signup",
            password="password",
        )

        cls.default_data = {"username": "sharkle", "password": "password"}

    def test_user_field_conflict(self):
        data = self.default_data.copy()
        data.update({"email": "signup@sharkle.com", "user_id": "new_id"})
        response = self.client.post(
            "/api/v1/auth/signup/", data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        response_data = response.json()
        self.assertEqual(["이미 가입된 이메일입니다."], response_data["email"])

    def test_missing_required_field(self):
        response = self.client.post(
            "/api/v1/auth/signup/",
            data=self.default_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_wrong_email_format(self):
        data = self.default_data.copy()
        data.update({"email": "invalid_format", "user_id": "email_invalid_user"})
        response = self.client.post(
            "/api/v1/auth/signup/", data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        response_data = response.json()
        self.assertEqual(["Enter a valid email address."], response_data["email"])

    def test_signup_success(self):
        data = {
            "email": "success@sharkle.com",
            "user_id": "success",
            "username": "success",
            "password": "password",
        }
        response = self.client.post(
            "/api/v1/auth/signup/", data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response_data = response.json()
        self.assertIn("refresh", response_data)
        self.assertIn("access", response_data)
        self.assertEqual(User.objects.count(), 2)


class PostLoginTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory(
            email="login@sharkle.com",
            user_id="login",
            username="login",
            password="password",
        )

    def test_login_fail(self):
        data = {"email": "login@sharkle.com", "password": "wrong!!!!"}
        response = self.client.post(
            "/api/v1/auth/login/", data=data, content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = response.json()
        self.assertEqual(
            response_data["detail"],
            "No active account found with the given credentials",
        )

    def test_login_success(self):
        data = {"email": "login@sharkle.com", "password": "password"}
        response = self.client.post(
            "/api/v1/auth/login/", data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn("refresh", response_data)
        self.assertIn("access", response_data)
