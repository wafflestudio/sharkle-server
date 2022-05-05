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

class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)  # 테스트용 임시

    # GET /account/{id}/
    def retrieve(self, request, pk):
        if pk == 'my':
            return Response(data=UserViewSerializer(request.data).data, status=status.HTTP_200_OK)
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
            return Response(
                status=status.HTTP_409_CONFLICT,
                data={"detail": "예상하지 못한 데이터베이스 에러가 발생했습니다."},
            )

        refresh_token = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
