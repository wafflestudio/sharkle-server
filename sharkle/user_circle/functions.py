from django.contrib.auth.models import AnonymousUser
from .models import UserCircleMember, UserCircleAlarm, Membership
from user.serializers import UserViewSerializer

def user_membership(circle, user):
    if isinstance(user, AnonymousUser):
        return "Anonymous", Membership.일반

    membership = ("일반", Membership.일반)
    user_circle_member = UserCircleMember.objects.get_or_none(user=user, circle=circle)

    if user_circle_member:
        membership = (Membership(user_circle_member.membership).name,
                      user_circle_member.membership)

    return membership


def user_status(circle, user):
    data = dict()
    data["user_info"] = UserViewSerializer(user).data
    data["membership"], data["membership_code"] = user_membership(circle, user)
    data["alarm"] = bool(UserCircleAlarm.objects.get_or_none(user=user, circle=circle))

    return data
