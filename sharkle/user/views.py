from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.serializers import UserSignUpSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from .serializers import UserViewSerializer
from .models import User
from common.exception_response import ExceptionResponse, ErrorCode
from django.contrib.auth.models import AnonymousUser


class UserViewSet(viewsets.GenericViewSet):
    #permission_classes = (permissions.IsAuthenticated,)  # 테스트용 임시
    permission_classes = (permissions.AllowAny, )

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
                    user = User.objects.get(user_id = user_id)
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
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
