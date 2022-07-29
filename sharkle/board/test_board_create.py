import factory
from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from board.board_test_factory import (
    NotMemberFactory,
    NotManagerFactory,
    ManagerFactory,
    CircleFactory,
    BoardFactory,
)
from board.models import Board
from user_circle.models import UserCircleMember, Membership
from rest_framework import status


class BoardCreateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = NotMemberFactory().user  # User1 is manager of circle
        cls.user2 = NotManagerFactory().user  # User2 is only member of circle
        cls.user3 = ManagerFactory().user  # User3 is not member of circle

        cls.circle = CircleFactory()

        UserCircleMember.objects.create(
            circle_id=cls.circle.id, user_id=cls.user1.id, membership=Membership.관리자
        )
        UserCircleMember.objects.create(
            circle_id=cls.circle.id, user_id=cls.user2.id, membership=Membership.회원
        )

        cls.board_data = {"name": "QnA", "is_private": False}

        cls.user1_token = "Bearer " + str(RefreshToken.for_user(cls.user1).access_token)
        cls.user2_token = "Bearer " + str(RefreshToken.for_user(cls.user2).access_token)
        cls.user3_token = "Bearer " + str(RefreshToken.for_user(cls.user3).access_token)

    def test_create_board_success(self):
        data = self.board_data.copy()
        token = self.user1_token
        before = Board.objects.count()
        response = self.client.post(
            f"/api/v1/circle/{self.circle.id}/board/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        after = Board.objects.count()
        self.assertEqual(before + 1, after)
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
