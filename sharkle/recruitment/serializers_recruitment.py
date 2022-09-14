from rest_framework import serializers
from .models import *
from schedule.serializers import ScheduleViewSerializer
from circle.functions import d_day_calculator

class RecruitmentInfoImageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruitmentInfoImage
        fields = ['info_image', 'sequence']

class RecruitmentViewSerializer(serializers.ModelSerializer):
    d_day = serializers.SerializerMethodField()
    d_day_detail = serializers.SerializerMethodField()
    info_images = serializers.SerializerMethodField()

    class Meta:
        model = Recruitment
        fields = ['id', 'circle', 'title', 'introduction', 'd_day', 'd_day_detail', 'title_image', 'info_images']

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

    def get_info_images(self, instance):
        images = RecruitmentInfoImage.objects.filter(recruitment=instance)
        return RecruitmentInfoImageViewSerializer(images, many=True).data

class RecruitmentUpdateSerializer(serializers.ModelSerializer):
    introduction = serializers.CharField(required=False, max_length=5000, allow_null=False, allow_blank=True)
    title = serializers.CharField(max_length=500, allow_null=False, allow_blank=True, required=False)
    info_image = serializers.ImageField(required=False)

    class Meta:
        model = Recruitment
        fields = ['introduction', 'title', 'title_image', 'info_image']


    def update(self, instance, validated_data):

        if 'title_image' in validated_data:
            instance.title_image.delete(save=False)

        if 'info_image' in validated_data:

            recruitment_info_images = RecruitmentInfoImage.objects.filter(recruitment=instance)
            for image in recruitment_info_images:
                image.info_image.delete(save=False)

            recruitment_info_images.delete()

            image_list = self.context.get('request').FILES.getlist('info_image')

            sequence = 0
            for image in image_list:
                RecruitmentInfoImage.objects.create(recruitment=instance, info_image=image, sequence=sequence)
                sequence += 1

        super().update(instance, validated_data)

class RecruitmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recruitment
        fields = ['circle', 'introduction', 'title', 'title_image']

    def create(self, validated_data):

        recruitment = super().create(validated_data)

        image_list = self.context.get('request').FILES.getlist('info_image')

        sequence = 0
        for image in image_list:
            RecruitmentInfoImage.objects.create(recruitment=recruitment, info_image=image, sequence=sequence)
            sequence += 1

        return recruitment
