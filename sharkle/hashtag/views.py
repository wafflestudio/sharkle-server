from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response

from common.exception_response import ExceptionResponse, ErrorCode
from .serializers import *
from .models import *


class HashTagViewSet(viewsets.GenericViewSet):
    serializer_class = HashtagSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET /hashtag/
    def list(self, request):
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = HashtagSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="Page is None",
                code=ErrorCode.PAGINATION_FAULT,
            ).to_response()

    def get_queryset(self):
        return Hashtag.objects.all()
