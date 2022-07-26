from rest_framework import viewsets, permissions, status

from .models import UserBoardAlarm, UserRecruitmentAlarm
from rest_framework.response import Response

from circle.functions import find_user, find_circle
from board.models import Board
from board.serializers import BoardSerializer
from .serializers import UserBoardAlarmSerializer
from .models import UserCircleAlarm, UserCircleMember, Membership

from .serializers import UserCircleViewSerializer
from user.models import User
from .functions import user_membership, user_status
from recruitment.models import Recruitment
from recruitment.serializers_recruitment import RecruitmentViewSerializer

# Create your views here.


class UserCircleViewSet(viewsets.GenericViewSet):
    serializer_class = UserCircleViewSerializer
    permission_classes = (permissions.AllowAny,)  # 테스트용 임시

    # GET /circle/{id}/user/
    def list(self, request, circle_id):

        error, circle = find_circle(circle_id)
        if error:
            return error

        users_type = {"가입신청":  User.objects.filter(membership__circle=circle, membership__membership=Membership.가입신청),
                      "회원": User.objects.filter(membership__circle=circle, membership__membership=Membership.회원),
                      "관리자": User.objects.filter(membership__circle=circle, membership__membership=Membership.관리자)}

        users = User.objects.none()

        if "membership" in request.query_params:
            membership = request.query_params.get("membership").split()
            for key in membership:
                if key in users_type:
                    sub_users = users_type[key]
                    users |= sub_users
        else:
            users = users_type["회원"] | users_type["관리자"]

        if "alarm" in request.query_params:
            alarm = request.query_params.get("alarm").lower()
            if alarm == "true":
                users = users.filter(subscribe__circle=circle)
            if alarm == "false":
                users = users.exclude(subscribe__circle=circle)

        page = self.paginate_queryset(users)
        return self.get_paginated_response(UserCircleViewSerializer(page, many=True, context={'circle': circle}).data)

class UserBoardAlarmViewSet(viewsets.GenericViewSet):
    queryset = UserBoardAlarm.objects.all()  # .... not appropriate?
    serializer_class = UserBoardAlarmSerializer
    permission_classes = (permissions.AllowAny,)  

    @classmethod
    def get_board_alarm_list(cls, circle, user):
        membership, membership_code = user_membership(circle, user)

        boards = Board.objects.filter(circle=circle)
        if membership_code < Membership.회원:
            boards = boards.filter(is_private=False)

        function = (lambda board: {"board_info": BoardSerializer(board).data,
                                   "board_alarm": bool(UserBoardAlarm.objects.get_or_none(user=user, board=board))})

        board_alarm = [function(board) for board in boards]
        return board_alarm

    @classmethod
    def get_recruitment_alarm_list(cls, circle, user):
        recruitments = Recruitment.objects.filter(circle=circle)

        function = (lambda recruitment:
                    {"recruitment_info": RecruitmentViewSerializer(recruitment).data,
                     "recruitment_alarm": bool(UserRecruitmentAlarm.objects.get_or_none
                                               (user=user, recruitment=recruitment))})

        recruitment_alarm = [function(recruitment) for recruitment in recruitments]
        return recruitment_alarm

    @classmethod
    def get_alarm_dict(cls, circle, user):
        data = {"alarm": user_status(circle, user)["alarm"]}
        if data["alarm"]:
            board_alarm = cls.get_board_alarm_list(circle, user)
            data["board_alarm"] = board_alarm
            data["board_alarm_count"] = len(board_alarm)

            recruitment_alarm = cls.get_recruitment_alarm_list(circle, user)
            data["recruitment_alarm"] = recruitment_alarm
            data["recruitment_alarm_count"] = len(recruitment_alarm)
        return data

    @classmethod
    def get_membership_dict(cls, circle, user):
        data = user_status(circle, user)
        return {"membership": data["membership"], "membership_code": data["membership_code"]}


    @classmethod
    def update_alarm(cls, circle, user, data):
        if "alarm" in data:
            if data['alarm']:
                UserCircleAlarm.objects.get_or_create(user=user, circle=circle)
            else:
                UserBoardAlarm.objects.filter(user=user, board__circle=circle).delete()
                UserRecruitmentAlarm.objects.filter(user=user, recruitment__circle=circle).delete()
                if user_circle_alarm := UserCircleAlarm.objects.get_or_none(
                        user=user, circle=circle
                ):
                    user_circle_alarm.delete()

        alarm_on = user_status(circle, user)["alarm"]

        if not alarm_on:
            return

        for key in data:
            if len(key) >= 9 and key[:9] == "board_id_":
                value = data[key]

                try:
                    board = Board.objects.get(id=key[9:], circle=circle)
                except Board.DoesNotExist:
                    continue
                except ValueError:
                    continue

                if value:
                    UserBoardAlarm.objects.get_or_create(user=user, board=board)

                else:
                    if user_board_alarm := UserBoardAlarm.objects.get_or_none(user=user, board=board):
                        user_board_alarm.delete()

        for key in data:
            if len(key) >= 15 and key[:15] == "recruitment_id_":
                value = data[key]

                try:
                    recruitment = Recruitment.objects.get(id=key[15:], circle=circle)
                except Recruitment.DoesNotExist:
                    continue
                except ValueError:
                    continue

                if value:
                    UserRecruitmentAlarm.objects.get_or_create(user=user, recruitment=recruitment)

                else:
                    if user_recruitment_alarm := \
                            UserRecruitmentAlarm.objects.get_or_none(user=user, recruitment=recruitment):
                        user_recruitment_alarm.delete()

    @classmethod
    def update_membership(cls, circle, user, data):

        membership_code, membership_code_ = None, None

        if "membership_code" in data:
            membership_code = data["membership_code"]
            if membership_code not in Membership.values:
                return

        if "membership" in data:
            membership = data["membership"]
            if membership not in UserCircleMember.membership_name_to_value:
                return
            membership_code_ = UserCircleMember.membership_name_to_value[membership]

        if membership_code_ is not None:
            if membership_code is not None and membership_code_ != membership_code:
                return
            membership_code = membership_code_

        if membership_code is None:
            return

        if membership_code == Membership.일반:
            if user_circle_member := UserCircleMember.objects.get_or_none(user=user, circle=circle):
                user_circle_member.delete()
        else:
            user_circle_member = UserCircleMember.objects.get_or_create(user=user, circle=circle)[0]

            user_circle_member.membership = membership_code
            user_circle_member.save()

    # GET /circle/{id}/user/{id}/
    def list(self, request, circle_id, user_id):
        error, circle = find_circle(circle_id)
        if error:
            return error

        error, user = find_user(user_id, request.user)
        if error:
            return error

        return Response(user_status(circle, user), status=status.HTTP_200_OK)


    # GET /circle/{id}/account/{id}/{pk}/
    def retrieve(self, request, circle_id, user_id, pk):
        error, circle = find_circle(circle_id)
        if error:
            return error

        error, user = find_user(user_id, request.user)
        if error:
            return error

        if pk == "alarm":
            return Response(self.get_alarm_dict(circle, user), status=status.HTTP_200_OK)
        if pk == "membership":
            return Response(self.get_membership_dict(circle, user), status=status.HTTP_200_OK)

    # PUT /circle/{id}/account/{id}/{pk}/
    def update(self, request, circle_id, user_id, pk):
        error, circle = find_circle(circle_id)
        if error:
            return error

        error, user = find_user(user_id, request.user)
        if error:
            return error

        if pk == "alarm":
            self.update_alarm(circle, user, request.data)
            return Response(self.get_alarm_dict(circle, user), status=status.HTTP_200_OK)

        if pk == "membership":
            self.update_membership(circle, user, request.data)
            return Response(self.get_membership_dict(circle, user), status=status.HTTP_200_OK)
