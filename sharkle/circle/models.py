from django.db import models
from user.models import CustomUser as User

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
    type = models.IntegerField()
    name = models.CharField(max_length=100, null=False, blank=False)
    bio = models.CharField(max_length=300, null=False, blank=True)
    homepage = models.ForeignKey(Homepage, on_delete=models.SET_NULL, null=True)
    introduction = models.CharField(max_length=5000, null=True, blank=True)
    tag = models.CharField(max_length=500, null=False, blank=True)

    def __str__(self):
        return self.name

class UserCircle_Member(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership', null=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='membership', null=True)
    is_manager = models.BooleanField()

class UserCircle_Alarm(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribe', null=True)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='subscribe', null=True)
