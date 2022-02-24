from django.db import models
from common.models import BaseModel
from board.models import Board
from user.models import CustomUser as User

class Article(BaseModel):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='articles', null=True)
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', null=True)

    title = models.CharField(max_length=100, null=False)
    text = models.CharField(max_length=1000, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        return "[" + str(self.id) + "] : " + self.title + " / " + self.text[0:20] + " ..."

class UserArticle(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_article', null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='user_article', null=False)
    like = models.BooleanField(default=False, null=False)
    scrap = models.BooleanField(default=False, null=False)
    alarm = models.BooleanField(default=False, null=False)
    nickname_code = models.PositiveSmallIntegerField(null=True)

    # nickname_code - 익명 표시
    # null : "익명"
    # 0 : 익명(글쓴이)
    # 1~ : 익명 1
