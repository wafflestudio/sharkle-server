from django.db import models
from user.models import User
from board.models import Board
from recruitment.models import Recruitment

from common.models import BaseModel
from circle.models import Circle


class Membership(models.IntegerChoices):
    일반 = 0, "일반"
    가입신청 = 1, "가입신청"
    회원 = 2, "회원"
    관리자 = 3, "관리자"


class UserCircleMember(BaseModel):
    membership = models.PositiveSmallIntegerField(choices=Membership.choices, default=Membership.회원)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="membership", null=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="membership", null=True)

    membership_name_to_value = {"일반": 0, "가입신청": 1, "회원": 2, "관리자": 3}

class UserCircleAlarm(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscribe", null=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="subscribe", null=True)

    live_recruitment_alarm = models.BooleanField(default=False)

class UserBoardAlarm(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscribe_board", null=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="subscribe_board", null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("user", "board"),
                name="Fields Set of UserBoardAlarm Should be Unique!"
            )
        ]