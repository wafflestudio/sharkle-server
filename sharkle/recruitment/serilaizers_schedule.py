from rest_framework import serializers, status
from .models import *
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from common.custom_exception import CustomException
from schedule.serializers import *

class RecruitScheduleViewSerializer(serializers.ModelSerializer):
    circle_id = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    recruitment_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    highlight = serializers.SerializerMethodField()
    d_day = serializers.BooleanField()

    class Meta:
        model = Schedule
        fields = ['id', 'circle_id', 'recruitment_id', 'name', 'start', 'end', 'location', 'highlight', 'd_day']

    def get_id(self, instance):
        return instance.schedule.id
    def get_recruitment_id(self, instance):
        return instance.recruitment.id
    def get_circle_id(self, instance):
        return instance.recruitment.circle.id
    def get_name(self, instance):
        return instance.schedule.name
    def get_start(self, instance):
        return instance.schedule.start
    def get_end(self, instance):
        return instance.schedule.end
    def get_location(self, instance):
        return instance.schedule.location
    def get_highlight(self, instance):
        return instance.schedule.highlight

class RecruitScheduleSerializer(serializers.ModelSerializer):
    recruitment = serializers.IntegerField()
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True)
    start = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)
    d_day = serializers.BooleanField(required=False)

    class Meta:
        model = RecruitmentSchedule
        fields = ['recruitment', 'name', 'start', 'end', 'location', 'highlight', 'd_day']

    def validate(self, data):
        if 'start' in data and 'end' in data:
            if data['start'] > data['end']:
                raise ValidationError({'end': "Start should be smaller then End"})

        return super().validate(data)


    def create(self, validated_data):

        recruitment = validated_data['recruitment']
        recruitment = Recruitment.objects.get(id=recruitment)

        validated_data['circle'] = recruitment.circle.id

        serializer = ScheduleSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()

        if 'd_day' in validated_data:
            d_day = validated_data['d_day']
            return RecruitmentSchedule.objects.create(recruitment=recruitment, schedule=schedule, d_day=d_day)
        return RecruitmentSchedule.objects.create(recruitment=recruitment, schedule=schedule)

class RecruitScheduleUpdateSerializer(RecruitScheduleSerializer):
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    start = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    highlight = serializers.BooleanField(required=False)
    d_day = serializers.BooleanField(required=False)

    class Meta:
        model = RecruitmentSchedule
        fields = ['name', 'start', 'end', 'location', 'highlight', 'd_day']

    def update(self, instance, validated_data):

        schedule = instance.schedule

        serializer = ScheduleUpdateSerializer(schedule, data=validated_data)
        serializer.is_valid(raise_exception=True)
        serializer.update(schedule, serializer.validated_data)

        return super().update(instance, validated_data)
