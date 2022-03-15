from django.db import models


# Create your models here.
class Board(models.Model):
    circle = models.SmallIntegerField(null=False)  # models.ForeignKey(Circle)
    name = models.CharField(max_length=20, blank=False)
    is_private = models.BooleanField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
