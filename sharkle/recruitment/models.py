from django.db import models
from common.models import BaseModel
from circle.models import Circle


class Recruitment(BaseModel):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='recruitment', null=False)
    introduction = models.CharField(max_length=5000, null=True, blank=True)

class RecruitmentSchedule(BaseModel):
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name='schedules', null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    start = models.DateTimeField()
    end = models.DateTimeField()
    location = models.CharField(max_length=100, null=False, blank=True)