from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response
from .serializers import *
from .models import *
from django.db.models import Q
from user.models import User

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
        print(circle)

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

        serializer = CircleUpdateSerializer(circle, data=request.data)
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


class UserCircleViewSet(viewsets.GenericViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET /circle/{id}/account/{id}/
    def list(self, request, circle_id, user_id):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if user_id == 'my':
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "유저가 존재하지 않습니다."})

        membership = UserCircle_Member.objects.get_or_none(user=user, circle=circle)
        alarm = UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)

        data = dict()

        data['membership'] = "일반"
        if membership:
            data['membership'] = "회원"
            if membership.is_manager:
                data['membership'] = "관리자"
        data['alarm'] = bool(alarm)

        return Response(status=status.HTTP_400_BAD_REQUEST, data=data)

    #GET /circle/{id}/account/{id}/{name}/
    def retrieve(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if user_id == 'my':
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "유저가 존재하지 않습니다."})

        if pk == 'alarm':
            return Response(status=status.HTTP_200_OK, data=bool(UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)))
        if pk == 'member':
            return Response(status=status.HTTP_200_OK, data=bool(UserCircle_Member.objects.get_or_none(user=user, circle=circle)))
        if pk == 'manager':
            return Response(status=status.HTTP_200_OK, data=bool(UserCircle_Member.objects.get_or_none(user=user, circle=circle, is_manager=True)))
        return Response(status=status.HTTP_200_OK)

    #PUT /circle/{id}/account/{id}/{name}/
    def update(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if user_id == 'my':
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "유저가 존재하지 않습니다."})

        if pk == 'alarm':
            UserCircle_Alarm.objects.get_or_create(user=user, circle=circle)

        if pk == 'member':
            UserCircle_Member.objects.get_or_create(user=user, circle=circle)

        if pk == 'manager':
            user_circle_member = UserCircle_Member.objects.get_or_create(user=user, circle=circle)[0]
            user_circle_member.is_manager = True
            user_circle_member.save()

        return Response(status=status.HTTP_200_OK,
                        data={"alarm": bool(UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)),
                              "member": bool(UserCircle_Member.objects.get_or_none(user=user, circle=circle)),
                              "manager": bool(UserCircle_Member.objects.get_or_none(user=user, circle=circle, is_manager=True))})

    # DELETE /circle/{id}/account/{id}/{name}/
    def delete(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."})

        if user_id == 'my':
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={"error": "wrong_id", "detail": "유저가 존재하지 않습니다."})

        if pk == 'alarm':
            if user_circle_alarm := UserCircle_Alarm.objects.get_or_none(user=user, circle=circle):
                user_circle_alarm.delete()

        if pk == 'member':
            if user_circle_member := UserCircle_Member.objects.get_or_none(user=user, circle=circle):
                user_circle_member.delete()

        if pk == 'manager':
            if user_circle_member := UserCircle_Member.objects.get_or_none(user=user, circle=circle):
                user_circle_member.is_manager = False
                user_circle_member.save()

        return Response(status=status.HTTP_200_OK,
                        data={"alarm": bool(UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)),
                              "member": bool(UserCircle_Member.objects.get_or_none(user=user, circle=circle)),
                              "manager": bool(
                                  UserCircle_Member.objects.get_or_none(user=user, circle=circle, is_manager=True))})




