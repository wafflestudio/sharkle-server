from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from circle.models import Circle, UserCircle_Member
from circle.serializers import CircleSerializer
from rest_framework import status

from user.serializers import UserSignUpSerializer


class TestUser:
    not_member_user = {
        "email": "notMemeber@snu.ac.kr",
        "password": "password",
        "username": "user1",
        "user_id": "user1",
    }

    not_manager_user = {
        "email": "notManager@snu.ac.kr",
        "password": "password",
        "username": "user2",
        "user_id": "user2",
    }

    manager_user = {
        "email": "Manager@snu.ac.kr",
        "password": "password",
        "username": "user3",
        "user_id": "user3",
    }


class TestCircle:
    circle = {
        "name": "waffle",
        "bio": "waffle_circle",
        "tag": "프로그래밍",
        "type0": 0,
        "type1": 0,
    }


class BoardCreateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_serializer1 = UserSignUpSerializer(data=TestUser.not_member_user)
        user_serializer1.is_valid()
        cls.user1 = user_serializer1.save()  # User1 is manager of circle
        user_serializer1.is_valid()
        user_serializer2 = UserSignUpSerializer(data=TestUser.not_manager_user)
        user_serializer2.is_valid()
        cls.user2 = user_serializer2.save()  # User2 is only member of circle
        user_serializer3 = UserSignUpSerializer(data=TestUser.manager_user)
        user_serializer3.is_valid()
        cls.user3 = user_serializer3.save()  # User3 is not member of circle

        circle_serializer = CircleSerializer(data=TestCircle.circle)
        circle_serializer.is_valid()
        cls.circle = circle_serializer.save()

        UserCircle_Member.objects.create(
            circle_id=cls.circle.id, user_id=cls.user1.id, is_manager=True
        )
        UserCircle_Member.objects.create(
            circle_id=cls.circle.id, user_id=cls.user2.id, is_manager=False
        )

        cls.board_data = {"name": "QnA", "is_private": False}

        cls.user1_token = "Bearer " + str(RefreshToken.for_user(cls.user1).access_token)
        cls.user2_token = "Bearer " + str(RefreshToken.for_user(cls.user2).access_token)
        cls.user3_token = "Bearer " + str(RefreshToken.for_user(cls.user3).access_token)

    def test_create_board_success(self):
        data = self.board_data.copy()
        token = self.user1_token
        response = self.client.post(
            f"/api/v1/circle/{self.circle.id}/board/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)

    def test_create_board_with_only_member_user(self):
        data = self.board_data.copy()
        token = self.user2_token
        response = self.client.post(
            f"/api/v1/circle/{self.circle.id}/board/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_board_with_not_member_user(self):
        data = self.board_data.copy()
        token = self.user3_token
        response = self.client.post(
            f"/api/v1/circle/{self.circle.id}/board/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
