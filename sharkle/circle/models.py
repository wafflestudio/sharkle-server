from django.db import models
from user.models import User

# Create your models here.
from common.models import BaseModel


class Homepage(BaseModel):
    homepage = models.CharField(max_length=500, null=True, blank=False)
    facebook = models.CharField(max_length=500, null=True, blank=False)
    instagram = models.CharField(max_length=500, null=True, blank=False)
    twitter = models.CharField(max_length=500, null=True, blank=False)
    youtube = models.CharField(max_length=500, null=True, blank=False)
    tiktok = models.CharField(max_length=500, null=True, blank=False)
    band = models.CharField(max_length=500, null=True, blank=False)


class Circle(BaseModel):
    class CircleType0(models.IntegerChoices):
        기타 = 0, "기타"
        연합 = 1, "연합"
        중앙 = 2, "중앙"
        단과대 = 3, "단과대"
        과 = 4, "과"

    type0 = models.PositiveSmallIntegerField(
        choices=CircleType0.choices, default=CircleType0.기타
    )

    class CircleType1(models.IntegerChoices):
        기타 = 0, "기타"
        학술매체 = 1, "학술/매체"
        연행예술 = 2, "연행/예술"
        취미교양 = 3, "취미/교양"
        무예운동 = 4, "무예/운동"
        인권봉사 = 5, "인권/봉사"
        종교 = 6, "종교"

    type1 = models.PositiveSmallIntegerField(
        choices=CircleType1.choices, default=CircleType1.기타
    )

    name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    bio = models.CharField(max_length=300, null=False, blank=True)
    homepage = models.ForeignKey(Homepage, on_delete=models.SET_NULL, null=True)

    introduction = models.CharField(max_length=5000, null=True, blank=True)
    tag = models.CharField(max_length=500, null=False, blank=True)

    class MakeNewMember(models.IntegerChoices):
        일반 = 0, "일반"  # 비회원 이상의 유저 초대 권한 가짐
        회원 = 1, "회원"  # 회원 이상의 유저 초대 권한 가짐
        관리자 = 2, "관리자"  # 관리자 이상의 유저 초대 권한 가짐

    make_new_member = models.PositiveSmallIntegerField(
        choices=MakeNewMember.choices, default=MakeNewMember.회원
    )

    def __str__(self):
        return self.name

class UserCircle_Member(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="membership", null=True
    )
    circle = models.ForeignKey(
        Circle, on_delete=models.CASCADE, related_name="membership", null=True
    )
    is_manager = models.BooleanField(default=False)


class UserCircle_Alarm(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribe", null=True
    )
    circle = models.ForeignKey(
        Circle, on_delete=models.CASCADE, related_name="subscribe", null=True
    )
