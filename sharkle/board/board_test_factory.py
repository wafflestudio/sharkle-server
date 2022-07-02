from factory.django import DjangoModelFactory

from board.models import Board
from circle.models import Circle
from user.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    @classmethod
    def create(cls, **kwargs):
        user = User.objects.create_user(**kwargs)
        return user


class NotMemberFactory:
    def __init__(self):
        self.user = UserFactory(
            email="notMemeber@snu.ac.kr",
            password="password",
            username="user1",
        )


class NotManagerFactory:
    def __init__(self):
        self.user = UserFactory(
            email="notmanager@snu.ac.kr",
            password="password",
            username="user2",
        )


class ManagerFactory:
    def __init__(self):
        self.user = UserFactory(
            email="Manager@snu.ac.kr",
            password="password",
            username="user3",
        )


class CircleFactory(DjangoModelFactory):
    class Meta:
        model = Circle

    name = "waffle"
    bio = "wafflr_circle"
    tag = "프로그래밍"
    type0 = 0
    type1 = 0


class BoardFactory(DjangoModelFactory):
    class Meth:
        model = Board

    @classmethod
    def create(cls, **kwargs):
        board = Board.objects.create(**kwargs)
        return board
