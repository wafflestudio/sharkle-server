from django.shortcuts import render
from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from .serializers import *

# Create your views here.
class RecruitmentViewSet(viewsets.GenericViewSet):
    serializer_class = RecruitmentSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

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

    def create(self, request, circle_id):

        data = request.data.copy()
        data['circle'] = circle_id

        serializer = self.get_serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        recruitment = serializer.save()

        return Response(status=status.HTTP_201_CREATED, data=RecruitmentViewSerializer(recruitment).data)

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
