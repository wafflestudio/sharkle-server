import datetime

from rest_framework import serializers, status
from .models import *
from django.core.exceptions import ValidationError, PermissionDenied
from common.custom_exception import CustomException
from schedule.serializers import ScheduleViewSerializer

def d_day_calculator(recruitment):
    schedules = RecruitmentSchedule.objects.filter(recruitment=recruitment, d_day=True)
    schedules_id = (i.schedule.id for i in schedules)
    schedules = Schedule.objects.filter(id__in=schedules_id).order_by("end")

    for i in schedules:
        if i.end.timestamp() - datetime.datetime.now().timestamp() > 0:
            return i
    return None

class RecruitmentViewSerializer(serializers.ModelSerializer):
    d_day = serializers.SerializerMethodField()
    d_day_detail = serializers.SerializerMethodField()
    class Meta:
        model = Recruitment
        fields = ['id', 'circle', 'title', 'introduction', 'd_day', 'd_day_detail']

    def get_d_day(self, instance):
        d_day = d_day_calculator(instance)
        if not d_day:
            return None
        return int((d_day.end.timestamp() - datetime.datetime.now().timestamp()) / 3600 / 24)

    def get_d_day_detail(self, instance):
        d_day = d_day_calculator(instance)
        if not d_day:
            return None
        return ScheduleViewSerializer(d_day).data

class RecruitmentUpdateSerializer(serializers.ModelSerializer):
    introduction = serializers.CharField(required=False, max_length=5000, allow_null=False, allow_blank=True)
    title = serializers.CharField(max_length=500, allow_null=False, allow_blank=True, required=False)

    class Meta:
        model = Recruitment
        fields = ['introduction', 'title']

class RecruitmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruitment
        fields = ['circle', 'introduction', 'title']
