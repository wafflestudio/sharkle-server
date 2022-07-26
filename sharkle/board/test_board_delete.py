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


class BoardDeleteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = NotMemberFactory().user  # User1 is manager of circle
        cls.user2 = NotManagerFactory().user  # User2 is only member of circle
        cls.user3 = ManagerFactory().user  # User3 is not member of circle

        cls.circle = CircleFactory()

        UserCircleMember.objects.create(
            circle=cls.circle, user=cls.user1, membership=Membership.관리자
        )
        UserCircleMember.objects.create(
            circle=cls.circle, user=cls.user2,  membership=Membership.회원
        )

        cls.user1_token = "Bearer " + str(RefreshToken.for_user(cls.user1).access_token)
        cls.user2_token = "Bearer " + str(RefreshToken.for_user(cls.user2).access_token)
        cls.user3_token = "Bearer " + str(RefreshToken.for_user(cls.user3).access_token)

        cls.open_board = BoardFactory(
            circle=cls.circle, name="open_QnA", is_private=False
        )

    def test_delete_board_success(self):
        token = self.user1_token
        before = Board.objects.count()
        response = self.client.delete(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        after = Board.objects.count()
        self.assertEqual(before, after + 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()

    def test_create_board_with_only_member_user(self):
        token = self.user2_token
        response = self.client.delete(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_board_with_not_member_user(self):
        token = self.user3_token
        response = self.client.delete(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token,
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
