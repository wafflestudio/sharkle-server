from rest_framework import serializers, status
from .models import *
from django.core.exceptions import ValidationError, PermissionDenied
from common.custom_exception import CustomException

class RecruitmentViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    circle_id = serializers.IntegerField()
    introduction = serializers.CharField()
    class Meta:
        model = Recruitment
        fields = ['id', 'circle_id', 'introduction']

    def get_circle_id(self, instance):
        return instance.circle.id

class RecruitmentUpdateSerializer(serializers.ModelSerializer):
    introduction = serializers.CharField(required=False, max_length=5000, allow_null=False, allow_blank=True)

    class Meta:
        model = Recruitment
        fields = ['introduction']

    def validate(self, data):
        if 'circle' in data:
            circle = int(data['circle'])
            if not (circle := Circle.objects.get_or_none(id=circle)):
                raise CustomException("존재하지 않는 Circle입니다", status.HTTP_404_NOT_FOUND)

        return super().validate(data)

    def update(self, instance, validated_data):
        if 'circle' in validated_data:
            validated_data['circle'] = Circle.objects.get_or_none(id=validated_data['circle'])
        #print(validated_data)
        return super().update(instance, validated_data)

class RecruitmentSerializer(serializers.ModelSerializer):
    circle = serializers.IntegerField()
    introduction = serializers.CharField(max_length=5000, allow_null=False, allow_blank=True)

    class Meta:
        model = Recruitment
        fields = ['circle', 'introduction']

    def validate(self, data):
        circle = int(data['circle'])
        if not (circle := Circle.objects.get_or_none(id=circle)):
            raise CustomException("존재하지 않는 Circle입니다", status.HTTP_404_NOT_FOUND)

        return super().validate(data)

    def create(self, validated_data):

        validated_data['circle'] = Circle.objects.get_or_none(id=validated_data['circle'])

        return super().create(validated_data)

class RecruitScheduleViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    recruitment_id = serializers.SerializerMethodField()
    circle_id = serializers.SerializerMethodField()
    name = serializers.CharField()
    start = serializers.DateTimeField()
    end = serializers.DateTimeField()
    location = serializers.CharField()

    class Meta:
        model = RecruitmentSchedule
        fields = ['id', 'circle_id', 'recruitment_id', 'name', 'start', 'end', 'location']

    def get_recruitment_id(self, instance):
        return instance.recruitment.id

    def get_circle_id(self, instance):
        return instance.recruitment.circle.id

class RecruitScheduleSerializer(serializers.ModelSerializer):
    recruitment = serializers.IntegerField()
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True)
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    end = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)

    class Meta:
        model = RecruitmentSchedule
        fields = ['recruitment', 'name', 'start', 'end', 'location']

    def validate(self, data):
        if 'start' in data and 'end' in data:
            if data['start'] > data['end']:
                raise ValidationError({'end': "Start should be smaller then End"})

        return super().validate(data)

    def create(self, validated_data):

        validated_data['recruitment'] = Recruitment.objects.get_or_none(id=validated_data['recruitment'])

        return super().create(validated_data)

class RecruitScheduleUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    end = serializers.DateTimeField(required=False, format="%Y-%m-%d %H:%M:%S")
    location = serializers.CharField(max_length=100, allow_null=False, allow_blank=True, required=False)

    class Meta:
        model = RecruitmentSchedule
        fields = ['name', 'start', 'end', 'location']

    def update(self, instance, validated_data):

        start = validated_data.get('start', instance.start)
        end = validated_data.get('end', instance.end)

        if start and end:
            if start > end:
                raise CustomException({"end": "Start should be smaller then End"},
                                      status_code=status.HTTP_400_BAD_REQUEST)

        return super().update(instance, validated_data)
