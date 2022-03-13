from rest_framework import serializers

from .models import Circle, Homepage
from hashtag.models import Hashtag, HashtagCircle


class HomepageSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    homepage = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    facebook = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    instagram = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    twitter = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    youtube = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    tiktok = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    band = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )

    class Meta:
        model = Homepage
        fields = [
            "id",
            "homepage",
            "facebook",
            "instagram",
            "twitter",
            "youtube",
            "tiktok",
            "band",
        ]
        # extra_fields = ['problems']


class CircleViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices)
    name = serializers.CharField()
    bio = serializers.CharField()

    homepage = serializers.SerializerMethodField()

    introduction = serializers.CharField()
    tag = serializers.CharField()

    class Meta:
        model = Circle
        fields = [
            "id",
            "type0",
            "type1",
            "name",
            "bio",
            "introduction",
            "tag",
            "homepage",
        ]
        # extra_fields = ['problems']

    def get_homepage(self, obj):
        return HomepageSerializer(obj.homepage).data


class CircleSerializer(serializers.ModelSerializer):
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices)
    name = serializers.CharField(max_length=100, allow_null=False, allow_blank=False)
    bio = serializers.CharField(
        max_length=300, allow_null=False, allow_blank=True, required=False
    )

    homepage = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    facebook = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    instagram = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    twitter = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    youtube = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    tiktok = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    band = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )

    introduction = serializers.CharField(
        max_length=5000, allow_null=True, allow_blank=True, required=False
    )
    tag = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=True, required=False
    )

    class Meta:
        model = Circle
        fields = [
            "type0",
            "type1",
            "name",
            "bio",
            "introduction",
            "tag",
        ] + HomepageSerializer.Meta.fields
        # extra_fields = ['problems']

    def create(self, validated_data):

        serializer = HomepageSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        homepage = serializer.save()

        for i in HomepageSerializer.Meta.fields:
            if i in validated_data:
                validated_data.pop(i)

        validated_data["homepage"] = homepage

        circle = Circle.objects.create(**validated_data)

        tags = circle.tag.split(" ")
        for tag in tags:
            if not (hashtag := Hashtag.objects.get_or_none(name=tag)):
                hashtag = Hashtag.objects.create(name=tag)
            if not (
                hashtag_circle := HashtagCircle.objects.get_or_none(
                    hashtag=hashtag, circle=circle
                )
            ):
                hashtag_circle = HashtagCircle.objects.create(
                    hashtag=hashtag, circle=circle
                )

        return circle


class CircleUpdateSerializer(serializers.ModelSerializer):
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices, required=False)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices, required=False)
    name = serializers.CharField(
        max_length=100, allow_null=False, allow_blank=False, required=False
    )
    bio = serializers.CharField(
        max_length=300, allow_null=False, allow_blank=True, required=False
    )

    homepage = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    facebook = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    instagram = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    twitter = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    youtube = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    tiktok = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )
    band = serializers.CharField(
        max_length=500, allow_null=True, allow_blank=False, required=False
    )

    introduction = serializers.CharField(
        max_length=5000, allow_null=True, allow_blank=True, required=False
    )
    tag = serializers.CharField(
        max_length=500, allow_null=False, allow_blank=True, required=False
    )

    class Meta:
        model = Circle
        fields = [
            "type0",
            "type1",
            "name",
            "bio",
            "introduction",
            "tag",
        ] + HomepageSerializer.Meta.fields
        # extra_fields = ['problems']

    def update(self, instance, validated_data):
        print(instance, validated_data)

        data = {}
        for i in HomepageSerializer.Meta.fields:
            if i in validated_data:
                data[i] = validated_data.pop(i)

        print(data, instance)

        serializer = HomepageSerializer(instance.homepage, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance.homepage, serializer.validated_data)

        # tag update
        if "tag" in validated_data:
            instance.tag = validated_data.pop("tag")
            tags = list(set(instance.tag.split(" ")))

            hashtags = [Hashtag.objects.get_or_create(name=tag)[0] for tag in tags]

            HashtagCircle.objects.filter(circle=instance).exclude(
                hashtag__in=hashtags
            ).delete()

            for hashtag in hashtags:
                hashtag_circle = HashtagCircle.objects.get_or_create(
                    circle=instance, hashtag=hashtag
                )

        return super().update(instance, validated_data)
