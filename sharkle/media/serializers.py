from rest_framework import serializers
from media.models import Image


class MultipleImageUploadSerializer(serializers.Serializer):
    def validate(self, data):
        images = self.context["request"].FILES.getlist("image")
        if not images:
            raise serializers.ValidationError("neither content nor media")
        return data

    def create(self, validated_data):
        image_list = self.context["request"].FILES.getlist("image")
        image_obj_list = []
        for image in image_list:
            if image is not None:
                image_obj_list.append(Image.objects.create(title="", image=image))

        return image_obj_list


class ImageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
