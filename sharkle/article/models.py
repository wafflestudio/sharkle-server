from django.db import models
from common.models import BaseModel
from board.models import Board
from user.models import User


class Article(BaseModel):
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, related_name="articles", null=True
    )  # null=True?
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="articles", null=True
    )
    is_private = models.BooleanField(default=False)
    title = models.CharField(max_length=20, blank=False)
    content = models.CharField(max_length=1000, blank=False)  # TODO blank=False null
    view = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
