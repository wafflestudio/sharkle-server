from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.response import Response

from common.exception_response import ExceptionResponse, ErrorCode
from .serilaizers_schedule import *
from .serializers_recruitment import *
from circle.functions import *
from circle.models import Circle

# Create your views here.


class RecruitmentViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitmentSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    def get_queryset(self):
        return Recruitment.objects.all()

    # GET circle/{id}/recruitment/
    def list(self, request, circle_id):

        error, circle = find_circle(circle_id)
        if error:
            return error

        queryset = self.get_queryset()
        queryset = queryset.filter(circle_id=circle_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecruitmentViewSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return ExceptionResponse(
                status=status.HTTP_400_BAD_REQUEST,
                detail="Page is None",
                code=ErrorCode.PAGINATION_FAULT,
            ).to_response()

    # GET circle/{id}/recruitment/{default, id}/
    def retrieve(self, request, circle_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(pk, circle)
        if error:
            return error

        return Response(
            status=status.HTTP_200_OK,
            data=RecruitmentViewSerializer(recruitment).data,
        )

    # POST circle/{id}/recruitment/
    def create(self, request, circle_id):

        recruitments = Recruitment.objects.filter(circle_id=circle_id)
        if len(recruitments) > 0:
            return ExceptionResponse(
                status=status.HTTP_409_CONFLICT,
                detail="동아리에 Recruitment가 이미 존재합니다.",
                code=ErrorCode.CONFLICT,
            ).to_response()

        data = request.data.copy()
        data["circle"] = circle_id

        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        recruitment = serializer.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data=RecruitmentViewSerializer(recruitment).data,
        )

    # PUT circle/{id}/recruitment/{default, id}
    def update(self, request, circle_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(pk, circle)
        if error:
            return error

        serializer = RecruitmentUpdateSerializer(recruitment, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.update(recruitment, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=RecruitmentViewSerializer(recruitment).data
        )

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, pk):
        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(pk, circle)
        if error:
            return error

        recruitment.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )


class RecruitmentScheduleViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitScheduleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET circle/{id}/recruitment/{id}/schedule/
    def list(self, request, circle_id, recruitment_id):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(recruitment_id, circle)
        if error:
            return error

        queryset = self.get_queryset().filter(recruitment=recruitment)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = RecruitScheduleViewSerializer(
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
        return RecruitmentSchedule.objects.all()

    # POST circle/{id}/recruitment/
    def create(self, request, circle_id, recruitment_id):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(recruitment_id, circle)
        if error:
            return error

        data = request.data.copy()
        data["recruitment"] = recruitment.id

        serializer = self.get_serializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        recruitment_schedule = serializer.save()

        return Response(
            status=status.HTTP_201_CREATED,
            data=RecruitScheduleViewSerializer(recruitment_schedule).data,
        )

    # PUT circle/{id}/recruitment/{id}/schedule/{id}
    def update(self, request, circle_id, recruitment_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(recruitment_id, circle)
        if error:
            return error

        error, recruitment_schedule = find_recruitment_schedule(pk, recruitment)
        if error:
            return error

        serializer = RecruitScheduleUpdateSerializer(
            recruitment_schedule, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(recruitment_schedule, serializer.validated_data)

        return Response(
            status=status.HTTP_201_CREATED,
            data=RecruitScheduleViewSerializer(recruitment_schedule).data,
        )

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, recruitment_id, pk):

        error, circle = find_circle(circle_id)
        if error:
            return error

        error, recruitment = find_recruitment(pk, circle)
        if error:
            return error

        error, recruitment_schedule = find_recruitment_schedule(pk, recruitment)
        if error:
            return error

        recruitment_schedule.schedule.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )


@api_view(("GET",))
@permission_classes((AllowAny,))
def get_recruitment_list_by_circle_name(request, circle_name):
    if not Circle.objects.filter(name=circle_name).exists():
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="name: " + circle_name + "에 해당하는 동아리가 존재하지 않습니다.",
            code=ErrorCode.CIRCLE_NOT_FOUND,
        ).to_response()
    circle = Circle.objects.get(name=circle_name)
    recruitment = Recruitment.objects.filter(circle=circle.id)
    return Response(RecruitmentSerializer(recruitment, many=True).data)
