from django.db import models


# Create your models here.
from circle.models import Circle


class Board(models.Model):
    class BoardType(models.IntegerChoices):
        일반 = 0, "일반"
        갤러리 = 1, "갤러리"

    type = models.PositiveSmallIntegerField(
        choices=BoardType.choices, default=BoardType.일반
    )

    circle = models.ForeignKey(
        Circle, on_delete=models.CASCADE, related_name="boards", null=True
    )
    name = models.CharField(max_length=20, blank=False)
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
