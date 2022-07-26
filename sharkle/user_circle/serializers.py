from rest_framework import serializers
from .models import UserBoardAlarm, UserRecruitmentAlarm
from board.serializers import BoardSerializer
from .models import UserCircleAlarm
from .functions import user_membership
from user.serializers import UserViewSerializer
from user.models import User
from .functions import user_status
from recruitment.serializers_recruitment import RecruitmentViewSerializer

class UserCircleViewSerializer(serializers.ModelSerializer):

    user_info = serializers.SerializerMethodField()
    membership = serializers.SerializerMethodField()
    membership_code = serializers.SerializerMethodField()
    alarm = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["user_info", "membership", "membership_code", "alarm"]

    def get_user_info(self, obj):
        circle = self.context.get("circle")
        return user_status(circle, obj)["user_info"]

    def get_alarm(self, obj):
        circle = self.context.get("circle")
        return bool(UserCircleAlarm.objects.get_or_none(user=obj, circle=circle))

    def get_membership(self, obj):
        circle = self.context.get("circle")
        return user_membership(circle, obj)[0]

    def get_membership_code(self, obj):
        circle = self.context.get("circle")
        return user_membership(circle, obj)[1]


class UserBoardAlarmSerializer(serializers.ModelSerializer):

    board_info = serializers.SerializerMethodField()

    class Meta:
        model = UserBoardAlarm
        fields = "__all__"
        extra_kwargs = {
            "board": {"required": True, "allow_null": False},
            "user": {"required": True, "allow_null": False},
        }

    def get_board_info(self, obj):
        board = obj.board
        return BoardSerializer(board).data


class UserRecruitmentAlarmSerializer(serializers.ModelSerializer):

    recruitment_info = serializers.SerializerMethodField()

    class Meta:
        model = UserRecruitmentAlarm
        fields = "__all__"
        extra_kwargs = {
            "recruitment": {"required": True, "allow_null": False},
            "user": {"required": True, "allow_null": False},
        }

    def get_recruitment_info(self, obj):
        recruitment = obj.recruitment
        return RecruitmentViewSerializer(recruitment).data
