from django.db import models
from common.models import BaseModel
from circle.models import Circle
from django.utils import timezone
from schedule.models import Schedule
from sharkle.upload_image import upload_image

class Recruitment(BaseModel):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='recruitment', null=False)
    title = models.CharField(max_length=500, null=False, blank=True)
    introduction = models.CharField(max_length=5000, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    title_image = models.ImageField(upload_to=upload_image, editable=True, null=True)

class RecruitmentInfoImage(BaseModel):
    sequence = models.IntegerField(default=-1, null=False)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name='recruitment_image', null=False)
    info_image = models.ImageField(upload_to=upload_image, editable=True, null=False)


class RecruitmentSchedule(BaseModel):
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, related_name='recruitment_schedule', null=True)
    recruitment = models.ForeignKey(Recruitment, on_delete=models.CASCADE, related_name='recruitment_schedule', null=False)
    d_day = models.BooleanField(default=False)