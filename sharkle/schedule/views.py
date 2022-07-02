from rest_framework import viewsets, permissions
from rest_framework.response import Response

from common.exception_response import ExceptionResponse, ErrorCode
from .models import *
from rest_framework import serializers, status
from .serializers import *
from circle.functions import *

# Create your views here.
class ScheduleViewSet(viewsets.GenericViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET circle/{id}/recruitment/{default, id}/
    def retrieve(self, request, circle_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, schedule = find_schedule(pk, circle)
        if error:
            return error

        return Response(
            status=status.HTTP_201_CREATED,
            data=ScheduleViewSerializer(schedule).data,
        )

    # GET circle/{id}/recruitment/
    def list(self, request, circle_id):

        query_params = request.query_params

        queryset = self.get_queryset()
        queryset = queryset.filter(circle_id=circle_id)

        if query_params.get('dday') == 'true':
            queryset = queryset.filter(d_day=True)
        elif query_params.get('dday') == 'false':
            queryset = queryset.filter(d_day=False)

        if query_params.get('highlight') == 'true':
            queryset = queryset.filter(highlight=True)
        elif query_params.get('highlight') == 'false':
            queryset = queryset.filter(highlight=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ScheduleViewSerializer(
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
        return Schedule.objects.all()

    # POST circle/{id}/recruitment/
    def create(self, request, circle_id):

        data = request.data.copy()
        data["circle"] = circle_id

        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        recruitment = serializer.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data=ScheduleViewSerializer(recruitment).data,
        )

    # PUT circle/{id}/recruitment/{default, id}
    def update(self, request, circle_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, schedule = find_schedule(pk, circle)
        if error:
            return error

        serializer = ScheduleUpdateSerializer(schedule, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(schedule, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=ScheduleViewSerializer(schedule).data
        )

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, pk):
        error, circle = find_circle(circle_id)
        if error:
            return error

        error, schedule = find_schedule(pk, circle)
        if error:
            return error

        schedule.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )