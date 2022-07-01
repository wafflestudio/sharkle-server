from rest_framework import status
from common.exception_response import ExceptionResponse, ErrorCode
from django.contrib.auth.models import AnonymousUser
from .models import *
from user.models import User
from hashtag.models import Hashtag, HashtagCircle

def update_hashtag(circle, hashtag_string):

    # 띄어쓰기를 기준으로 문자열을 쪼갬
    tags = list(set(hashtag_string.split(" ")) - {""})

    # 각 단어에 해당하는 Hashtag 인스턴스들을 불러옴
    hashtags = [Hashtag.objects.get_or_create(name=tag)[0] for tag in tags]  # (<Hashtag: Hashtag object (6)>, False)

    # 문자열에 포함되지 않은 단어와 연결된 HastagCircle 인스턴스들을 지움
    HashtagCircle.objects.filter(circle=circle).exclude(hashtag__in=hashtags).delete()

    # 각 단어와 circle을 연결해 HashtagCircle 인스턴스들을 만듬
    for hashtag in hashtags:
        hashtag_circle = HashtagCircle.objects.get_or_create(circle=circle, hashtag=hashtag)

def is_string_integer(str):
    if not str:
        return True
    for i in str.split(" "):
        try:
            int(i)
        except ValueError:
            return False
    return True

def find_circle(circle_id):
    # 존재하지 않는 동아리
    if not (circle := Circle.objects.get_or_none(id=circle_id)):
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
            code=ErrorCode.CIRCLE_NOT_FOUND,
        ).to_response(), None

    return None, circle


def find_user(user_id, my):
    # user 불러오기
    if user_id == "my":
        user = my
    elif User.objects.filter(id=user_id):
        user = User.objects.get(id=user_id)
    else:
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="id: " + user_id + "에 해당하는 유저가 존재하지 않습니다.",
            code=ErrorCode.USER_NOT_FOUND,
        ).to_response(), None

    # Anonymous User 에러
    if isinstance(user, AnonymousUser):
        return ExceptionResponse(
            status=status.HTTP_400_BAD_REQUEST,
            detail="로그인하지 않은 상태입니다. ",
            code=ErrorCode.ANONYMOUS_USER,
        ).to_response(), None

    return None, user

def user_membership(circle, user):
    if isinstance(user, AnonymousUser):
        return "Anonymous", 0

    membership = ("일반", 0)
    user_circle_member = UserCircle_Member.objects.get_or_none(user=user, circle=circle)

    if user_circle_member:
        membership = ("회원", 1)
        if user_circle_member.is_manager:
            membership = ("관리자", 2)

    return membership

def user_status(circle, user):
    data = dict()
    data["user_id"] = user.id
    data["membership"], data["membership_code"] = user_membership(circle, user)
    data["alarm"] = bool(UserCircle_Alarm.objects.get_or_none(user=user, circle=circle))

    return data