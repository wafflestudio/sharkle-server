from rest_framework import viewsets, permissions
from rest_framework.response import Response

from common.exception_response import ExceptionResponse, ErrorCode
from .serilaizers_schedule import *
from .serializers_recruitment import *


def get_circle_recruitment(circle_id, recruitment_id):

    # 존재하지 않는 Circle
    if not (circle := Circle.objects.get_or_none(id=circle_id)):
        return None, None

    # Recruitment (Default)
    if recruitment_id == "default":
        recruitments = Recruitment.objects.filter(circle=circle)
        # 동아리에 Recuritment가 존재하지 않음
        if not recruitments:
            return circle, None
        recruitment = recruitments.last()
    # Recruitment (id)
    else:
        recruitment = Recruitment.objects.get_or_none(id=recruitment_id, circle=circle)
    return circle, recruitment


def get_error_circle_recruitment(circle_id, recruitment_id):
    circle, recruitment = get_circle_recruitment(circle_id, recruitment_id)
    error = None

    if not circle:
        error = ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
            code=ErrorCode.CIRCLE_NOT_FOUND,
        ).to_response()
    elif not recruitment:
        error = ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="id: "
                   + str(recruitment_id)
                   + "에 해당하는 Recruitment가 존재하지 않습니다.",
            code=ErrorCode.RECRUITMENT_NOT_FOUND,
        ).to_response()

    return error, circle, recruitment


# Create your views here.
class RecruitmentViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitmentSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    def get_queryset(self):
        return Recruitment.objects.all()

    # GET circle/{id}/recruitment/
    def list(self, request, circle_id):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

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
        error, circle, recruitment = get_error_circle_recruitment(circle_id, pk)
        if error:
            return error

        print(error, type(error))

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
                code=ErrorCode.CONFLICT
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

        error, circle, recruitment = get_error_circle_recruitment(circle_id, pk)
        if error:
            return error

        serializer = RecruitmentUpdateSerializer(recruitment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(recruitment, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=RecruitmentViewSerializer(recruitment).data
        )

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, pk):
        error, circle, recruitment = get_error_circle_recruitment(circle_id, pk)
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

        print(recruitment_id)

        error, circle, recruitment = get_error_circle_recruitment(circle_id, recruitment_id)
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

        error, circle, recruitment = get_error_circle_recruitment(circle_id, recruitment_id)
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

        error, circle, recruitment = get_error_circle_recruitment(circle_id, recruitment_id)
        if error:
            return error

        if not (schedule := RecruitmentSchedule.objects.get_or_none(schedule__id=pk, recruitment=recruitment)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="Schedule이 존재하지 않습니다.",
                code=ErrorCode.SCHEDULE_NOT_FOUND,
            ).to_response()

        serializer = RecruitScheduleUpdateSerializer(schedule, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(schedule, serializer.validated_data)

        return Response(
            status=status.HTTP_201_CREATED,
            data=RecruitScheduleViewSerializer(schedule).data,
        )

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, recruitment_id, pk):

        error, circle, recruitment = get_error_circle_recruitment(circle_id, recruitment_id)
        if error:
            return error

        if not (recruitSchedule := RecruitmentSchedule.objects.get_or_none(schedule__id=pk, recruitment=recruitment)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="Schedule이 존재하지 않습니다.",
                code=ErrorCode.SCHEDULE_NOT_FOUND,
            ).to_response()

        recruitSchedule.schedule.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )
