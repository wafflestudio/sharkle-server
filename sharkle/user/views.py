from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from user.serializers import UserSignUpSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class PingPongView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response(data={"ping": "pong"}, status=status.HTTP_200_OK)


# Create user and return refresh & access token
class SignUpView(APIView):
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh_token = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh_token),
            "access": str(refresh_token.access_token),
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
