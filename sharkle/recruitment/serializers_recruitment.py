from rest_framework import serializers
from .models import *
from schedule.serializers import ScheduleViewSerializer
from circle.functions import d_day_calculator

class RecruitmentViewSerializer(serializers.ModelSerializer):
    d_day = serializers.SerializerMethodField()
    d_day_detail = serializers.SerializerMethodField()
    class Meta:
        model = Recruitment
        fields = ['id', 'circle', 'title', 'introduction', 'd_day', 'd_day_detail']

    def get_d_day(self, instance):
        d_day_schedule, d_day_days = d_day_calculator(instance)
        if d_day_days == "ERROR":
            return None
        return d_day_days

    def get_d_day_detail(self, instance):
        d_day_schedule, d_day_days = d_day_calculator(instance)
        if d_day_schedule == "ERROR":
            return None
        return ScheduleViewSerializer(d_day_schedule).data

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
