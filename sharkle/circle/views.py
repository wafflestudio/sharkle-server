from rest_framework import serializers, status, viewsets, permissions
from rest_framework.response import Response

from common.exception_response import ExceptionResponse, ErrorCode
from .serializers import *
from .models import *
from django.db.models import Q
from user.models import User

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
        # print(circle)
        qna_board = Board(circle=circle, name="QnA", is_private=False)
        qna_board.save()
        comm_board = Board(circle=circle, name="Community", is_private=True)
        comm_board.save()
        return Response(
            status=status.HTTP_201_CREATED, data=CircleViewSerializer(circle).data
        )

    # GET /circle/{id}/
    def retrieve(self, request, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        return Response(
            status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data
        )

    # PUT /circle/{id}/
    def put(self, request, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        serializer = CircleUpdateSerializer(circle, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(circle, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=CircleViewSerializer(circle).data
        )

    # DELETE /circle/{id}/
    def destroy(self, instance, pk):
        if not (circle := Circle.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        circle.delete()

        return Response(
            status=status.HTTP_200_OK, data={"detail": "deleted successfully"}
        )

    def is_string_integeralbe(self, str):
        if not str:
            return True
        for i in str.split(" "):
            try:
                int(i)
            except ValueError:
                return False
        return True

    # GET /circle/
    def list(self, request):
        queryset = self.get_queryset()

        error = {}
        for i in ["tag", "type0", "type1"]:
            str = request.query_params.get(i, None)
            if not self.is_string_integeralbe(str):
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


class UserCircleViewSet(viewsets.GenericViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET /circle/{id}/account/
    def list(self, request, circle_id):
        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "동아리가 존재하지 않습니다."},
            )

        option = request.query_params.get("option", None)

        objects = dict()
        objects["manager"] = UserCircle_Member.objects.filter(
            is_manager=True, circle=circle
        )
        objects["member"] = UserCircle_Member.objects.filter(
            is_manager=False, circle=circle
        )
        objects["all_member"] = UserCircle_Member.objects.filter(circle=circle)
        objects["alarm"] = UserCircle_Alarm.objects.filter(circle=circle)

        if option in ("alarm",):
            page = self.paginate_queryset(objects[option])
            return self.get_paginated_response(UserStatus_A(page, many=True).data)

        if option in (
            "member",
            "manager",
            "all_member",
        ):
            page = self.paginate_queryset(objects[option])
            return self.get_paginated_response(UserStatus_M(page, many=True).data)

        return Response(status=status.HTTP_400_BAD_REQUEST, data="pagination fault")


class UserCircleUpdateSet(viewsets.GenericViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시
    # GET /circle/{id}/account/{id}/
    def list(self, request, circle_id, user_id):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        if user_id == "my":
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + user_id + "에 해당하는 유저가 존재하지 않습니다.",
                code=ErrorCode.USER_NOT_FOUND,
            ).to_response()

        membership = UserCircle_Member.objects.get_or_none(user=user, circle=circle)
        alarm = UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)

        data = dict()

        data["membership"] = "일반"
        if membership:
            data["membership"] = "회원"
            if membership.is_manager:
                data["membership"] = "관리자"
        data["alarm"] = bool(alarm)

        return Response(status=status.HTTP_200_OK, data=data)

    # GET /circle/{id}/account/{id}/{name}/
    def retrieve(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        if user_id == "my":
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + user_id + "에 해당하는 유저가 존재하지 않습니다.",
                code=ErrorCode.USER_NOT_FOUND,
            ).to_response()

        if pk == "alarm":
            return Response(
                status=status.HTTP_200_OK,
                data=bool(
                    UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)
                ),
            )
        if pk == "member":
            return Response(
                status=status.HTTP_200_OK,
                data=bool(
                    UserCircle_Member.objects.get_or_none(user=user, circle=circle)
                ),
            )
        if pk == "manager":
            return Response(
                status=status.HTTP_200_OK,
                data=bool(
                    UserCircle_Member.objects.get_or_none(
                        user=user, circle=circle, is_manager=True
                    )
                ),
            )
        return Response(status=status.HTTP_200_OK)

    # PUT /circle/{id}/account/{id}/{name}/
    def update(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        if user_id == "my":
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + user_id + "에 해당하는 유저가 존재하지 않습니다.",
                code=ErrorCode.USER_NOT_FOUND,
            ).to_response()

        if pk == "alarm":
            UserCircle_Alarm.objects.get_or_create(user=user, circle=circle)

        if pk == "member":
            UserCircle_Member.objects.get_or_create(user=user, circle=circle)

        if pk == "manager":
            user_circle_member = UserCircle_Member.objects.get_or_create(
                user=user, circle=circle
            )[0]
            user_circle_member.is_manager = True
            user_circle_member.save()

        return Response(
            status=status.HTTP_200_OK,
            data={
                "alarm": bool(
                    UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)
                ),
                "member": bool(
                    UserCircle_Member.objects.get_or_none(user=user, circle=circle)
                ),
                "manager": bool(
                    UserCircle_Member.objects.get_or_none(
                        user=user, circle=circle, is_manager=True
                    )
                ),
            },
        )

    # DELETE /circle/{id}/account/{id}/{name}/
    def delete(self, request, circle_id, user_id, pk):

        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        if user_id == "my":
            user = request.user
        elif User.objects.filter(id=user_id):
            user = User.objects.get(id=user_id)
        else:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + user_id + "에 해당하는 유저가 존재하지 않습니다.",
                code=ErrorCode.USER_NOT_FOUND,
            ).to_response()

        if pk == "alarm":
            if user_circle_alarm := UserCircle_Alarm.objects.get_or_none(
                user=user, circle=circle
            ):
                user_circle_alarm.delete()

        if pk == "member":
            if user_circle_member := UserCircle_Member.objects.get_or_none(
                user=user, circle=circle
            ):
                user_circle_member.delete()

        if pk == "manager":
            if user_circle_member := UserCircle_Member.objects.get_or_none(
                user=user, circle=circle
            ):
                user_circle_member.is_manager = False
                user_circle_member.save()

        return Response(
            status=status.HTTP_200_OK,
            data={
                "alarm": bool(
                    UserCircle_Alarm.objects.get_or_none(user=user, circle=circle)
                ),
                "member": bool(
                    UserCircle_Member.objects.get_or_none(user=user, circle=circle)
                ),
                "manager": bool(
                    UserCircle_Member.objects.get_or_none(
                        user=user, circle=circle, is_manager=True
                    )
                ),
            },
        )


class IntroViewSet(viewsets.ViewSet):
    serializer_class = CircleSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    def retrieve(self, request, circle_id):
        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        return Response(
            status=status.HTTP_200_OK, data=CircleIntroSerializer(circle).data
        )

    def update(self, request, circle_id):
        if not (circle := Circle.objects.get_or_none(id=circle_id)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                code=ErrorCode.CIRCLE_NOT_FOUND,
            ).to_response()

        serializer = CircleIntroSerializer(circle, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(circle, serializer.validated_data)

        return Response(
            status=status.HTTP_200_OK, data=CircleIntroSerializer(circle).data
        )
