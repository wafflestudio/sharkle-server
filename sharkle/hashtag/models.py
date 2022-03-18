from django.db import models
from circle.models import Circle

# Create your models here.
from common.models import BaseModel

# Create your models here.
class Hashtag(BaseModel):
    name = models.CharField(max_length=100)


class HashtagCircle(BaseModel):
    hashtag = models.ForeignKey(
        Hashtag, on_delete=models.CASCADE, null=False, related_name="hashtag_circles"
    )
    circle = models.ForeignKey(
        Circle, on_delete=models.CASCADE, null=True, related_name="hashtag_circles"
    )
