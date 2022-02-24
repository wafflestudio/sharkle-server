from django.db import models
from circle.models import Circle

# Create your models here.
from common.models import BaseModel

# Create your models here.
class Hashtag(BaseModel):
    tag = models.CharField(max_length=100)

class HashtagCircle(BaseModel):
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE, null=False)
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, null=True)