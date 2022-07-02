from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.serializers import UserSignUpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from .serializers import (
    UserViewSerializer,
    EmailSerializer,
    UsernameSerializer,
    PasswordSerializer,
)
from .models import User
from common.exception_response import ExceptionResponse, ErrorCode


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)  # 테스트용 임시

    # GET /account/{id}/
    def retrieve(self, request, pk):
        if pk == "my":
            return Response(
                data=UserViewSerializer(request.data).data, status=status.HTTP_200_OK
            )
        user = User.objects.get(id=pk)
        return Response(data=UserViewSerializer(user).data, status=status.HTTP_200_OK)


class PingPongView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response(data={"ping": "pong"}, status=status.HTTP_200_OK)


# Create user and return refresh & access token
class SignUpView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
        except IntegrityError:
            return ExceptionResponse(
                status=status.HTTP_409_CONFLICT,
                detail="예상하지 못한 데이터베이스 에러가 발생했습니다.",
                code=ErrorCode.DATABASE_ERROR,
            ).to_response()

        refresh_token = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }
        return Response(data=data, status=status.HTTP_201_CREATED)


# Duplicate Check
class DuplicateEmailCheckView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_duplicate():
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="이미 데이터베이스에 존재하는 이메일입니다.",
                code=ErrorCode.DATABASE_ERROR,
            ).to_response()
        return Response(data={"detail": "사용 가능한 이메일입니다."}, status=status.HTTP_200_OK)


class DuplicateUsernameCheckView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UsernameSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_duplicate():
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="이미 데이터베이스에 존재하는 유저명입니다.",
                code=ErrorCode.DATABASE_ERROR,
            ).to_response()
        return Response(data={"detail": "사용 가능한 사용자 이름입니다."}, status=status.HTTP_200_OK)


class PasswordValidationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = PasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not serializer.is_valid_password_form():
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="비밀번호 형식 조건에 맞지 않습니다",
                code=ErrorCode.PASSWORD_FORMAT_INVALID,
            ).to_response()

        return Response(data={"detail": "사용 가능한 비밀번호입니다."}, status=status.HTTP_200_OK)
