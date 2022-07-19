import factory
from django.test import TestCase
from factory.django import DjangoModelFactory
from rest_framework_simplejwt.tokens import RefreshToken
from circle.models import Circle
from user.models import User
from rest_framework import status


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user%d" % n)
    email = factory.LazyAttribute(lambda o: "%s@sharkle.org" % o.username)
    password = "1234"


class CircleFactory(DjangoModelFactory):
    class Meta:
        model = Circle

    name = factory.Sequence(lambda n: "Circle %d" % n)
    bio = factory.Sequence(lambda n: "Circle %d bio" % n)
    tag = "sample_tag"


class GetCircleByNameTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.circle = CircleFactory()
        cls.user_token = "Bearer " + str(RefreshToken.for_user(cls.user).access_token)

    def test_get_circle_success(self):
        response = self.client.get(
            f"/api/v1/circle/{self.circle.name}/name/",
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=self.user_token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
