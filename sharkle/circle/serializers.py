from rest_framework import serializers
from user.models import User

from .models import *
from hashtag.models import Hashtag, HashtagCircle
from .functions import user_membership, update_hashtag, d_day_calculator
from rest_framework.validators import UniqueTogetherValidator
from recruitment.models import Recruitment
from schedule.serializers import ScheduleViewSerializer


class HomepageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    homepage = serializers.CharField(max_length=500, allow_null=True, required=False)
    facebook = serializers.CharField(max_length=500, allow_null=True, required=False)
    instagram = serializers.CharField(max_length=500, allow_null=True, required=False)
    twitter = serializers.CharField(max_length=500, allow_null=True, required=False)
    youtube = serializers.CharField(max_length=500, allow_null=True, required=False)
    tiktok = serializers.CharField(max_length=500, allow_null=True, required=False)
    band = serializers.CharField(max_length=500, allow_null=True, required=False)

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


class UserStatus_M(serializers.ModelSerializer):
    id = serializers.IntegerField()
    alarm = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    membership_code = serializers.SerializerMethodField()

    class Meta:
        model = UserCircle_Member
        fields = ["id", "alarm", "membership", "membership_code"]

    def get_id(self, obj):
        return obj.user.id

    def get_alarm(self, obj):
        return bool(
            UserCircle_Alarm.objects.get_or_none(user=obj.user, circle=obj.circle)
        )

    def get_membership(self, obj):
        return user_membership(obj.circle, obj.user)[0]

    def get_membership_code(self, obj):
        return user_membership(obj.circle, obj.user)[1]


class UserStatus_A(UserStatus_M):
    class Meta:
        model = UserCircle_Alarm
        fields = ["id", "alarm", "membership", "membership_code"]


class CircleViewSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices)
    name = serializers.CharField()
    bio = serializers.CharField()

    homepage = serializers.SerializerMethodField()

    introduction = serializers.CharField()
    tag = serializers.CharField()
    tag_integer = serializers.SerializerMethodField()

    d_day = serializers.SerializerMethodField()
    d_day_detail = serializers.SerializerMethodField()

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
            "tag_integer",
            "homepage",
            "d_day",
            "d_day_detail",
        ]
        # extra_fields = ['problems']

    def get_d_day(self, instance):
        recruitment = Recruitment.objects.get_or_none(circle=instance)
        if recruitment is None:
            return None
        d_day_schedule, d_day_days = d_day_calculator(recruitment)
        if d_day_days == "ERROR":
            return None
        return d_day_days

    def get_d_day_detail(self, instance):
        recruitment = Recruitment.objects.get_or_none(circle=instance)
        if recruitment is None:
            return None
        d_day_schedule, d_day_days = d_day_calculator(recruitment)
        if d_day_schedule == "ERROR":
            return None
        return ScheduleViewSerializer(d_day_schedule).data

    def get_homepage(self, obj):
        return HomepageSerializer(obj.homepage).data

    def get_tag_integer(self, obj):
        query = HashtagCircle.objects.filter(circle=obj)
        return [hc.hashtag.id for hc in query]


class CircleSerializer(serializers.ModelSerializer):
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices)
    name = serializers.CharField(max_length=100)

    homepage = serializers.CharField(max_length=500, allow_null=True, required=False)
    facebook = serializers.CharField(max_length=500, allow_null=True, required=False)
    instagram = serializers.CharField(max_length=500, allow_null=True, required=False)
    twitter = serializers.CharField(max_length=500, allow_null=True, required=False)
    youtube = serializers.CharField(max_length=500, allow_null=True, required=False)
    tiktok = serializers.CharField(max_length=500, allow_null=True, required=False)
    band = serializers.CharField(max_length=500, allow_null=True, required=False)

    bio = serializers.CharField(max_length=300, allow_blank=True, required=False)
    introduction = serializers.CharField(max_length=5000, allow_null=True, allow_blank=True, required=False)
    tag = serializers.CharField(max_length=500, allow_blank=True, required=False)

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
        validators = [
            UniqueTogetherValidator(queryset=Circle.objects.all(), fields=["name"])
        ]

    def create(self, validated_data):

        serializer = HomepageSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        homepage = serializer.save()

        for i in HomepageSerializer.Meta.fields:
            if i in validated_data:
                validated_data.pop(i)

        validated_data["homepage"] = homepage

        circle = Circle.objects.create(**validated_data)

        update_hashtag(circle, circle.tag)

        return circle


class CircleUpdateSerializer(CircleSerializer):
    type0 = serializers.ChoiceField(choices=Circle.CircleType0.choices, required=False)
    type1 = serializers.ChoiceField(choices=Circle.CircleType1.choices, required=False)
    name = serializers.CharField(max_length=100, required=False)

    def update(self, instance, validated_data):
        data = {}
        for i in HomepageSerializer.Meta.fields:
            if i in validated_data:
                data[i] = validated_data.pop(i)

        serializer = HomepageSerializer(instance.homepage, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.update(instance.homepage, serializer.validated_data)

        # tag update
        if "tag" in validated_data:
            instance.tag = validated_data.pop("tag")
            update_hashtag(instance, instance.tag)

        return super().update(instance, validated_data)


class CircleIntroSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=False)
    bio = serializers.CharField(
        max_length=300, allow_null=False, allow_blank=True, required=False
    )
    introduction = serializers.CharField(
        max_length=5000, allow_null=True, allow_blank=True, required=False
    )

    class Meta:
        model = Circle
        fields = [
            "id",
            "name",
            "bio",
            "introduction",
        ]
