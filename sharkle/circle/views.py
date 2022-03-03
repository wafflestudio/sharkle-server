from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from .models import Circle, Homepage
from django.db.models import Q

class HomepageViewSet(viewsets.GenericViewSet):
    serializer_class = HomepageSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # POST /homepage/
    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK, data=serializer.data)

class CircleViewSet(viewsets.GenericViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # POST /circle/
    def create(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        circle = serializer.save()

        return Response(status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data)

    # GET /circle/{id}/
    def retrieve(self, request, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        return Response(status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data)

    # PUT /circle/{id}/
    def put(self, request, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        serializer = CircleSerializer(circle, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(circle, serializer.validated_data)

        return Response(status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data)

    # DELETE /circle/{id}/
    def destroy(self, instance, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        circle.delete()

        return Response(status=status.HTTP_200_OK, data={"detail": "deleted successfully"})

    # GET /circle/
    def list(self, request):
        queryset = self.get_queryset()

        #name 검색
        search = request.query_params.get('name', None)
        queryset = self.get_queryset_search(search, queryset)

        #tag 검색
        if 'tag' in request.query_params:
            try:
                tag = int(request.query_params.get('tag'))
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="tag is not an integer")

            q = Q()
            for i in HashtagCircle.objects.filter(id=tag):
                print(i.circle)
                q &= Q(id=i.circle.id)

            if q:
                queryset = queryset.filter(q)
            else:
                queryset = Circle.objects.none()

        #type0 검색
        if 'type0' in request.query_params:
            try:
                type0 = int(request.query_params.get('type0'))
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="type0 is not an integer")
            queryset = queryset.filter(type0=type0)

        # type1 검색
        if 'type1' in request.query_params:
            try:
                type1 = int(request.query_params.get('type1'))
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="type1 is not an integer")
            queryset = queryset.filter(type1=type1)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CircleViewSerializer(page, many=True, context={'request': request})
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
            keywords = set(search.split(' '))
            for k in keywords:
                q &= Q(name__icontains=k)
            queryset = queryset.filter(q)
        return queryset.distinct()
