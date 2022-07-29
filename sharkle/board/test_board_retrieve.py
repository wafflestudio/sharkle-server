from django.test import TestCase
from rest_framework_simplejwt.tokens import RefreshToken

from board.board_test_factory import (
    NotMemberFactory,
    NotManagerFactory,
    ManagerFactory,
    CircleFactory,
    BoardFactory,
)
from user_circle.models import UserCircleMember, Membership
from rest_framework import status


class BoardRetrieveTestCase(TestCase):
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

        cls.private_board = BoardFactory(
            circle=cls.circle, name="private_QnA", is_private=True
        )
        cls.open_board = BoardFactory(
            circle=cls.circle, name="open_QnA", is_private=False
        )

    def test_retrieve_open_board_success_with_user1(self):
        token1 = self.user1_token
        token2 = self.user2_token
        token3 = self.user3_token
        response1 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token1,
        )
        response2 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token2,
        )
        response3 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.open_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token3,
        )
        # user 1 test
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        response_data = response1.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)
        # user 2 test
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        response_data = response2.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)
        # user 3 test
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        response_data = response3.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)

    def test_retrieve_private_board_success(self):
        token1 = self.user1_token
        token2 = self.user2_token
        response1 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.private_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token1,
        )
        response2 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.private_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token2,
        )
        # user 1 test
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        response_data = response1.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)
        # user 2 test
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        response_data = response2.json()
        self.assertIn("id", response_data)
        self.assertIn("name", response_data)

    def test_retrieve_private_board_fail(self):
        token3 = self.user3_token
        response3 = self.client.get(
            f"/api/v1/circle/{self.circle.id}/board/{self.private_board.id}/",
            content_type="application/json",
            HTTP_AUTHORIZATION=token3,
        )
        self.assertEqual(response3.status_code, status.HTTP_401_UNAUTHORIZED)
