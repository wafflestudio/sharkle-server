from rest_framework import serializers, status
from .models import *
from django.core.exceptions import ValidationError, PermissionDenied
from common.custom_exception import CustomException
from recruitment.models import RecruitmentSchedule


class ScheduleViewSerializer(serializers.ModelSerializer):
    is_recruitment = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'circle', 'name', 'start', 'end', 'location', 'highlight', 'is_recruitment',]

    def get_is_recruitment(self, instance):
        return bool(RecruitmentSchedule.objects.get_or_none(schedule=instance))


class ScheduleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, allow_blank=True)
    start = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)

    class Meta:
        model = Schedule
        fields = ['circle', 'name', 'start', 'end', 'location', 'highlight', ]

    def validate(self, data):
        if 'start' in data and 'end' in data:
            if data['start'] > data['end']:
                raise ValidationError({'end': "Start should be smaller then End"})

        return super().validate(data)


class ScheduleUpdateSerializer(ScheduleSerializer):
    name = serializers.CharField(max_length=100, allow_blank=True, required=False)
    start = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)

    class Meta:
        model = Schedule
        fields = ['name', 'start', 'end', 'location', 'highlight',]

