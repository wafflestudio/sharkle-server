from django.db import models
from user.models import User

# Create your models here.
from common.models import BaseModel


class Homepage(BaseModel):
    homepage = models.CharField(max_length=500, null=True, blank=True)
    facebook = models.CharField(max_length=500, null=True, blank=True)
    instagram = models.CharField(max_length=500, null=True, blank=True)
    twitter = models.CharField(max_length=500, null=True, blank=True)
    youtube = models.CharField(max_length=500, null=True, blank=True)
    tiktok = models.CharField(max_length=500, null=True, blank=True)
    band = models.CharField(max_length=500, null=True, blank=True)


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

    def __str__(self):
        return self.name
