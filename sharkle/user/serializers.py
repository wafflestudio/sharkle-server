from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    TokenObtainPairSerializer,
)
from user.models import User


class UserSignUpSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate_email(self, data):
        email = data.get("email")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("이미 가입된 이메일입니다.")

    def create(self, validated_data):
        username = validated_data.get("username")
        user_id = validated_data.get("user_id")
        email = validated_data.get("email")
        password = validated_data.get("password")
        user = User.objects.create_user(
            username=username, user_id=user_id, email=email, password=password
        )

        return user
