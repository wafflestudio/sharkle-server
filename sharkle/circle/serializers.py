from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Circle, Homepage
from hashtag.models import Hashtag, HashtagCircle

class CircleSerializer(serializers.ModelSerializer):
    type = serializers.IntegerField()
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=False)
    bio = serializers.CharField(max_length=300, allow_null=False, allow_blank=True, required=False)

    homepage = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    facebook = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    instagram = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    twitter = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    youtube = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    tiktok = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)
    band = serializers.CharField(max_length=500, allow_null=True, allow_blank=False, required=False)

    introduction = serializers.CharField(max_length=5000, allow_null=True, allow_blank=True, required=False)
    tag = serializers.CharField(max_length=500, allow_null=False, allow_blank=True, required=False)

    class Meta:
        model = Circle
        fields = ['type', 'name', 'bio', 'introduction', 'tag'] \
                 + ['homepage', 'facebook', 'instagram', 'twitter', 'youtube', 'tiktok', 'band']
        #extra_fields = ['problems']

    def create(self, validated_data):

        homepage_data = {}
        for i in ['homepage', 'facebook', 'instagram', 'twitter', 'youtube', 'tiktok', 'band']:
            if i in validated_data:
                homepage_data[i] = validated_data.pop(i)

        validated_data['homepage'] = Homepage.objects.create(**homepage_data)

        circle = Circle.objects.create(**validated_data)

        tags = circle.tag.split(' ')
        for tag in tags:
            if not (hashtag := Hashtag.objects.get_or_none(tag=tag)):
                hashtag = Hashtag.objects.create(tag=tag)
            if not (hashtag_circle := HashtagCircle.objects.get_or_none(hashtag=hashtag, circle=circle)):
                hashtag_circle = HashtagCircle.objects.create(hashtag=hashtag, circle=circle)

        return circle
