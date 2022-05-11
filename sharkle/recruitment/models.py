from django.db import models
from common.models import BaseModel
from circle.models import Circle
from django.utils import timezone
from schedule.models import Schedule



class Recruitment(BaseModel):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='recruitment', null=False)
    introduction = models.CharField(max_length=5000, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class RecruitmentSchedule(BaseModel):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='recruitment_schedule', null=False)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name='recruitment_schedule', null=False)

