from rest_framework import serializers, status
from .models import *
from django.core.exceptions import ValidationError, PermissionDenied
from common.custom_exception import CustomException
from recruitment.models import RecruitmentSchedule


class ScheduleViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    circle_id = serializers.SerializerMethodField()
    name = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    location = serializers.CharField()
    highlight = serializers.BooleanField()
    d_day = serializers.BooleanField()
    is_recruitment = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'circle_id', 'name', 'start', 'end', 'location', 'highlight', 'd_day', 'is_recruitment',]

    def get_circle_id(self, instance):
        return instance.circle.id
    def get_is_recruitment(self, instance):
        return bool(RecruitmentSchedule.objects.get_or_none(schedule=instance))


class ScheduleSerializer(serializers.ModelSerializer):
    circle = serializers.IntegerField()
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True)
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)
    d_day = serializers.BooleanField(required=False)

    class Meta:
        model = Schedule
        fields = ['circle', 'name', 'start', 'end', 'location', 'highlight', 'd_day', ]

    def validate(self, data):
        if 'start' in data and 'end' in data:
            if data['start'] > data['end']:
                raise ValidationError({'end': "Start should be smaller then End"})

        return super().validate(data)

    def create(self, validated_data):
        validated_data['circle'] = Circle.objects.get_or_none(id=validated_data['circle'])

        return super().create(validated_data)

class ScheduleUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    end = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)
    d_day = serializers.BooleanField(required=False)

    class Meta:
        model = Schedule
        fields = ['name', 'start', 'end', 'location', 'highlight', 'd_day',]

    def update(self, instance, validated_data):

        start = validated_data.get('start', instance.start)
        end = validated_data.get('end', instance.end)

        if start and end:
            if start > end:
                raise CustomException({"end": "Start should be smaller then End"},
                                      status_code=status.HTTP_400_BAD_REQUEST)

        return super().update(instance, validated_data)
