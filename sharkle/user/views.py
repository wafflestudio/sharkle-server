from django.shortcuts import render

# Create your views here.
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView


class PingPongView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response(data={"ping": "pong"}, status=status.HTTP_200_OK)
