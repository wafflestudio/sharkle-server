from django.db import models
from common.models import BaseModel
from article.models import Article
from user.models import User


class Comment(BaseModel):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="comments", null=True
    )  # null=True?
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="comments", null=True
    )
    content = models.CharField(max_length=1000, blank=False)  # TODO blank=False null
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey(
        "self", on_delete=models.PROTECT, related_name="replies", null=True
    )  # TODO SET_NULL?
    is_deleted = models.BooleanField(default=False)
