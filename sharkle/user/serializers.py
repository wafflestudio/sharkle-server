import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    TokenObtainPairSerializer,
)
from user.models import User


class UserViewSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)
    username = serializers.CharField()
    email = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")
        return email

    def create(self, validated_data):
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")
        user = User.objects.create_user(
            username=username, email=email, password=password
        )

        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def is_duplicate(self):
        return (
            True
            if User.objects.filter(email=self.validated_data["email"]).exists()
            else False
        )


class UsernameSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def is_duplicate(self):
        return (
            True
            if User.objects.filter(username=self.validated_data["username"]).exists()
            else False
        )


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)

    def is_valid_password_form(self):
        pwd = self.data["password"]

        if len(pwd) < 9:
            return False

        special_m = re.findall("[!@#$%^&*?+~]", pwd)  # special_chars = '!@#$%^&*?+~'
        alpha_m = re.findall("[a-zA-Z]", pwd)
        num_m = re.findall("[0-9]", pwd)
        unallowed_m = re.findall("[^0-9a-zA-A!@#$%^&*?+~]", pwd)

        if special_m and alpha_m and num_m and not unallowed_m:
            return True
        return False
