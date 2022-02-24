from django.db import models
from article.models import Article
from user.models import CustomUser as User
from common.models import BaseModel

class Comment(BaseModel):

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    is_subcomment = models.BooleanField(default=False, null = False)

    text = models.CharField(max_length=300, null = False)
    created_at = models.DateTimeField(auto_now_add=True)
    commenter = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='comments', null = True)

    is_writer = models.BooleanField(default=False, null = False)
    is_anonymous = models.BooleanField(default=True, null = False)
    is_active = models.BooleanField(default=True, null = False)

    def __str__(self):
        return self.text

class UserComment(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user_comment', null = True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='user_comment', null = False)
    like = models.BooleanField(default = False, null = False)
    subscribe = models.BooleanField(default = False, null = False)