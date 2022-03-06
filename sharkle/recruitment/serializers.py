from rest_framework import serializers, status
from .models import *
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
        print(validated_data)
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

        print(validated_data)

        validated_data['circle'] = Circle.objects.get_or_none(id=validated_data['circle'])

        return super().create(validated_data)

