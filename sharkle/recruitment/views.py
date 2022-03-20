from django.shortcuts import render
from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from .serializers import *

# Create your views here.
class RecruitmentViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitmentSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    #GET circle/{id}/recruitment/{default, id}/
    def retrieve(self, request, circle_id, pk):
        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if pk == 'default':
            recruitments = Recruitment.objects.filter(circle=circle)
            if not recruitments:
                Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})
            recruitment = recruitments.last()
        elif not (recruitment := Recruitment.objects.get_or_none(id=pk, circle=circle)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})

        return Response(status=status.HTTP_201_CREATED, data=RecruitmentViewSerializer(recruitment).data)

    #GET circle/{id}/recruitment/
    def list(self, request, circle_id):

        queryset = self.get_queryset()
        queryset = queryset.filter(circle_id=circle_id)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecruitmentViewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="pagination fault")

    def get_queryset(self):
        return Recruitment.objects.all()

    # POST circle/{id}/recruitment/
    def create(self, request, circle_id):

        data = request.data.copy()
        data['circle'] = circle_id

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recruitment = serializer.save()

        return Response(status=status.HTTP_201_CREATED, data=RecruitmentViewSerializer(recruitment).data)

    # PUT circle/{id}/recruitment/{default, id}
    def update(self, request, circle_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if pk == 'default':
            recruitments = Recruitment.objects.filter(circle=circle)
            if not recruitments:
                Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})
            recruitment = recruitments.last()
        elif not (recruitment := Recruitment.objects.get_or_none(id=pk, circle=circle)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})

        serializer = RecruitmentUpdateSerializer(recruitment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(recruitment, serializer.validated_data)

        return Response(status=status.HTTP_200_OK, data=RecruitmentViewSerializer(recruitment).data)

    # DELETE circle/{id}/recruitment/{default, id}
    def destroy(self, request, circle_id, pk):
        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if pk == 'default':
            recruitments = Recruitment.objects.filter(circle=circle)
            if not recruitments:
                Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})
            recruitment = recruitments.last()
        elif not (recruitment := Recruitment.objects.get_or_none(id=pk, circle=circle)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "Recruitment가 존재하지 않습니다."})

        recruitment.delete()

        return Response(status=status.HTTP_200_OK, data={"detail": "deleted successfully"})

class RecruitScheduleViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitScheduleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    def get_circle_recruitment(self, circle_id, recruitment_id):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return {"circle": None, "recruitment": None}

        if recruitment_id == 'default':
            recruitments = Recruitment.objects.filter(circle=circle)
            if not recruitments:
                return {"circle": circle, "recruitment": None}
            recruitment = recruitments.last()
        elif not (recruitment := Recruitment.objects.get_or_none(id=recruitment_id, circle=circle)):
            return {"circle": circle, "recruitment": None}

        return {"circle": circle, "recruitment": recruitment}

    # GET circle/{id}/recruitment/{id}/schedule/{id}
    def retrieve(self, request, circle_id, recruitment_id, pk):

        data = self.get_circle_recruitment(circle_id, recruitment_id)
        circle, recruitment = data["circle"], data["recruitment"]

        for i in ['circle', 'recruitment']:
            if not data[i]:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={"error": "wrong_id", "detail": i+"이 존재하지 않습니다."})

        if not (schedule := RecruitmentSchedule.objects.get_or_none(id=pk, recruitment=recruitment)):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={"error": "wrong_id", "detail": "Schedule이 존재하지 않습니다."})

        return Response(status=status.HTTP_201_CREATED, data=RecruitScheduleViewSerializer(schedule).data)

    # DELETE circle/{id}/recruitment/{id}/schedule/{id}
    def destroy(self, request, circle_id, recruitment_id, pk):

        data = self.get_circle_recruitment(circle_id, recruitment_id)
        circle, recruitment = data["circle"], data["recruitment"]

        for i in ['circle', 'recruitment']:
            if not data[i]:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={"error": "wrong_id", "detail": i + "이 존재하지 않습니다."})

        if not (schedule := RecruitmentSchedule.objects.get_or_none(id=pk, recruitment=recruitment)):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={"error": "wrong_id", "detail": "Schedule이 존재하지 않습니다."})

        schedule.delete()

        return Response(status=status.HTTP_200_OK, data={"detail": "deleted successfully"})

    # GET circle/{id}/recruitment/{id}/schedule/
    def list(self, request, circle_id, recruitment_id):

        data = self.get_circle_recruitment(circle_id, recruitment_id)
        circle, recruitment = data["circle"], data["recruitment"]

        for i in ['circle', 'recruitment']:
            if not data[i]:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={"error": "wrong_id", "detail": i + "이 존재하지 않습니다."})

        queryset = self.get_queryset()
        queryset = queryset.filter(recruitment=recruitment)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RecruitScheduleViewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="pagination fault")

    def get_queryset(self):
        return RecruitmentSchedule.objects.all()

    # POST circle/{id}/recruitment/{id}/schedule/
    def create(self, request, circle_id, recruitment_id):

        data = self.get_circle_recruitment(circle_id, recruitment_id)
        circle, recruitment = data["circle"], data["recruitment"]

        for i in ['circle', 'recruitment']:
            if not data[i]:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={"error": "wrong_id", "detail": i + "이 존재하지 않습니다."})

        data = request.data.copy()
        data['recruitment'] = recruitment.id

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recruitment_schedule = serializer.save()

        return Response(status=status.HTTP_201_CREATED, data=RecruitScheduleViewSerializer(recruitment_schedule).data)

    #PUT circle/{id}/recruitment/{id}/schedule/{id}
    def update(self, request, circle_id, recruitment_id, pk):

        data = self.get_circle_recruitment(circle_id, recruitment_id)
        circle, recruitment = data["circle"], data["recruitment"]

        for i in ['circle', 'recruitment']:
            if not data[i]:
                return Response(status=status.HTTP_404_NOT_FOUND,
                                data={"error": "wrong_id", "detail": i + "이 존재하지 않습니다."})

        if not (schedule := RecruitmentSchedule.objects.get_or_none(id=pk, recruitment=recruitment)):
            return Response(status=status.HTTP_404_NOT_FOUND,
                            data={"error": "wrong_id", "detail": "Schedule이 존재하지 않습니다."})

        serializer = RecruitScheduleUpdateSerializer(schedule, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(schedule, serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED, data=RecruitScheduleViewSerializer(schedule).data)
