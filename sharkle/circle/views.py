from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exception_response import ExceptionResponse, ErrorCode
from .serializers import *
from .models import *
from django.db.models import Q
from .functions import (
    find_circle,
    find_user,
    is_string_integer,
    d_day_calculator_circle_sort,
    find_circle_string,
)

from board.serializers import BoardSerializer

from board.models import Board


class HomepageViewSet(viewsets.GenericViewSet):
    serializer_class = HomepageSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # POST /homepage/
    def create(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK, data=serializer.data)


class CircleViewSet(viewsets.GenericViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # POST /circle/
    def create(self, request):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        circle = serializer.save()

        qna_board = Board(circle=circle, name="QnA", is_private=False)
        qna_board.save()
        comm_board = Board(circle=circle, name="Community", is_private=True)
        comm_board.save()

        return Response(
            status=status.HTTP_201_CREATED, data=CircleViewSerializer(circle).data
        )

    # GET /circle/{id}/
    def retrieve(self, request, pk):
        error, circle = find_circle(pk)
        if error:
            return error

        return Response(
            status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data
        )

    # PUT /circle/{id}/
    def put(self, request, pk):
        error, circle = find_circle(pk)
        if error:
            return error

        serializer = CircleUpdateSerializer(circle, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(circle, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data
        )

    # DELETE /circle/{id}/
    def destroy(self, instance, pk):
        error, circle = find_circle(pk)
        if error:
            return error

        circle.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )

    # GET /circle/
    def list(self, request):
        queryset = self.get_queryset()

        error = {}
        for i in ["tag", "type0", "type1"]:
            str = request.query_params.get(i, None)
            if not is_string_integer(str):
                error[i] = i + " is not integer"
        if error:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=error)

        # name 검색
        search = request.query_params.get("name", None)
        queryset = self.get_queryset_search(search, queryset)

        # tag 검색
        if request.query_params.get("tag", None):
            tags = request.query_params.get("tag")
            tags = tags.split(" ")

            for tag in tags:
                q = Q(pk__in=[])
                for i in HashtagCircle.objects.filter(hashtag__id=int(tag)):
                    q |= Q(id=i.circle.id)
                queryset = queryset.filter(q)

        # tag_str 검색
        if request.query_params.get("tag_str", None):
            strings = request.query_params.get("tag_str")
            strings = strings.split(" ")

            for string in strings:
                q = Q(pk__in=[])

                for i in HashtagCircle.objects.filter(hashtag__name=string):
                    q |= Q(id=i.circle.id)
                queryset = queryset.filter(q)

        # type0 검색
        if "type0" in request.query_params:
            if not request.query_params.get("type0"):
                queryset = queryset.none()
            else:
                q = Q()
                type0s = request.query_params.get("type0").split(" ")
                for type0 in type0s:
                    q |= Q(type0=int(type0))
                queryset = queryset.filter(q)

        # type1 검색
        if "type1" in request.query_params:
            if not request.query_params.get("type1"):
                queryset = queryset.none()
            else:
                q = Q()
                type1s = request.query_params.get("type1").split(" ")
                for type1 in type1s:
                    q |= Q(type1=int(type1))
                queryset = queryset.filter(q)

        # d_day sorting
        if "d_day" in request.query_params:
            if request.query_params.get("d_day") == "true":
                queryset = sorted(queryset, key=d_day_calculator_circle_sort)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CircleViewSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="pagination fault")

    def get_queryset(self):
        return Circle.objects.all()

    def get_queryset_search(self, search, queryset):
        if search == "":
            return Circle.objects.none()
        if search:
            q = Q()
            keywords = set(search.split(" "))
            for k in keywords:
                q &= Q(name__icontains=k)
            queryset = queryset.filter(q)
        return queryset.distinct()


class CircleNameView(APIView):
    permission_classes = (permissions.AllowAny,)

    # GET /circle/{circle_name}/name
    def get(self, request, circle_name):
        error, circle = find_circle_string(circle_name)
        if error:
            return error

        return Response(
            status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data
        )



class IntroViewSet(viewsets.ViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    def retrieve(self, request, circle_id):
        error, circle = find_circle(circle_id)
        if error:
            return error

        return Response(
            status=status.HTTP_200_OK, data=CircleIntroSerializer(circle).data
        )

    def update(self, request, circle_id):
        error, circle = find_circle(circle_id)
        if error:
            return error

        serializer = CircleIntroSerializer(circle, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(circle, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=CircleIntroSerializer(circle).data
        )
