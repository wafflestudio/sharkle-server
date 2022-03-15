from django.db import models


# Create your models here.
from circle.models import Circle


class Board(models.Model):
    circle_id = models.ForeignKey(
        Circle, on_delete=models.CASCADE, related_name="boards"
    )  # models.ForeignKey(Circle)
    name = models.CharField(max_length=20, blank=False)
    is_private = models.BooleanField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
