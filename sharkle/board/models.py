from django.db import models
from common.models import BaseModel
from circle.models import Circle


class Board(BaseModel):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='boards', null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    manager_editable = models.BooleanField(default=False, null=False)
    allow_anonymous = models.BooleanField(default=True, null=False)
