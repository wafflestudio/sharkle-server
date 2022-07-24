from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.serializers import UserSignUpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import IntegrityError
from .serializers import (
    UserViewSerializer,
    EmailSerializer,
    UsernameSerializer,
    PasswordSerializer,
)
from .models import User
from common.exception_response import ExceptionResponse, ErrorCode
from django.contrib.auth.models import AnonymousUser


class UserViewSet(viewsets.GenericViewSet):
    # permission_classes = (permissions.IsAuthenticated,)  # 테스트용 임시
    permission_classes = (permissions.AllowAny,)

    # GET /account/
    def list(self, request):

        query_params = request.query_params

        queryset = User.objects.all()

        if "username" in query_params:
            username = query_params.get("username")
            queryset = queryset.filter(username__icontains=username)

        if "user_id" in query_params:
            user_id = query_params.get("user_id")
            queryset = queryset.filter(user_id__icontains=user_id)

        if "email" in query_params:
            email = query_params.get("email")
            queryset = queryset.filter(email__icontains=email)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserViewSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="Page is None",
                code=ErrorCode.PAGINATION_FAULT,
            ).to_response()

    # GET /account/{id}/
    def retrieve(self, request, pk):

        user = None

        if pk == "my":
            user = request.user

        elif pk == "find":
            query_params = request.query_params
            if "user_id" in query_params:
                user_id = query_params.get("user_id")
                try:
                    user = User.objects.get(user_id=user_id)
                except Exception as e:
                    user = None
            if "email" in query_params:
                email = query_params.get("email")
                try:
                    user = User.objects.get(email=email)
                except Exception as e:
                    user = None

        else:
            try:
                user = User.objects.get(id=id)
            except Exception as e:
                user = None

        if not user:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="주어진 요청에 해당하는 유저가 존재하지 않습니다.",
                code=ErrorCode.USER_NOT_FOUND,
            ).to_response()

        if isinstance(user, AnonymousUser):
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="로그인하지 않은 상태입니다. ",
                code=ErrorCode.ANONYMOUS_USER,
            ).to_response()

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
            "username": serializer.data["username"],
            "email": serializer.data["email"],
        }
        return Response(data=data, status=status.HTTP_201_CREATED)

# Create user and return refresh & access token
class SignInView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        data = serializer.validated_data
        user = User.objects.get(email=request.data["email"])
        data["username"] = user.username
        data["email"] = request.data["email"]
        return Response(data, status=status.HTTP_200_OK)

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
