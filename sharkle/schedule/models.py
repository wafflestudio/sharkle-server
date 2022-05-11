from django.db import models
from common.models import BaseModel
from circle.models import Circle
from django.utils import timezone

# Create your models here.
class Schedule(BaseModel):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='schedule', null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, null=False, blank=True)
    highlight = models.BooleanField(default=False)
    d_day = models.BooleanField(default=False)