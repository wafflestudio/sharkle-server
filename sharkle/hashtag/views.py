from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.db.models import Q
from user.models import User


class HashTagViewSet(viewsets.GenericViewSet):
    serializer_class = HashtagSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET /circle/
    def list(self, request):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HashtagSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="pagination fault")

    def get_queryset(self):
        return Hashtag.objects.all()
