from rest_framework import status
from common.exception_response import ExceptionResponse, ErrorCode
from django.contrib.auth.models import AnonymousUser
from .models import *
from user.models import User
from hashtag.models import Hashtag, HashtagCircle
from enum import Enum
from recruitment.models import Recruitment, RecruitmentSchedule
from schedule.models import Schedule
import datetime
import math

def d_day_calculator_circle_sort(circle):
    recruitment = Recruitment.objects.get_or_none(circle=circle)
    if recruitment is None:
        return math.inf

    d_day_schedule, d_day_days = d_day_calculator(recruitment)
    if d_day_days == "ERROR":
        return math.inf

    return d_day_days

def d_day_calculator(recruitment):
    schedules = RecruitmentSchedule.objects.filter(recruitment=recruitment, d_day=True)
    schedules_id = (i.schedule.id for i in schedules)
    schedules = Schedule.objects.filter(id__in=schedules_id).order_by("end")

    for schedule in schedules:
        timestamp = schedule.end.timestamp() - datetime.datetime.now().timestamp()
        date = schedule.end.date() - datetime.date.today()

        if timestamp > 0:
            return schedule, date.days
    return "ERROR", "ERROR"

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


def find_recruitment(recruitment_id, circle):
    if recruitment_id == "default":
        recruitments = Recruitment.objects.filter(circle=circle)
        # 동아리에 Recuritment가 존재하지 않음
        if not recruitments:
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: "
                   + str(recruitment_id)
                   + "에 해당하는 Recruitment가 존재하지 않습니다.",
                code=ErrorCode.RECRUITMENT_NOT_FOUND,
            ).to_response(), None
        recruitment = recruitments.last()
    else:
        recruitment = Recruitment.objects.get_or_none(id=recruitment_id, circle=circle)
    return None, recruitment


def find_recruitment_schedule(schedule_id, recruitment):
    if not (recruitSchedule := RecruitmentSchedule.objects.get_or_none(schedule__id=schedule_id, recruitment=recruitment)):
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="Schedule이 존재하지 않습니다.",
            code=ErrorCode.SCHEDULE_NOT_FOUND,
        ).to_response(), None

    return None, recruitSchedule


def find_schedule(schedule_id, circle):
    if not (schedule := Schedule.objects.get_or_none(id=schedule_id, circle=circle)):
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="id: " + str(schedule_id) + "에 해당하는 Schedule가 존재하지 않습니다.",
            code=ErrorCode.RECRUITMENT_NOT_FOUND,
        ).to_response(), None

    return None, schedule

def find_circle_string(circle_name):
    # 존재하지 않는 동아리
    if not (circle := Circle.objects.get_or_none(name=circle_name)):
        return ExceptionResponse(
            status=status.HTTP_404_NOT_FOUND,
            detail="name: " + circle_name + "에 해당하는 동아리가 존재하지 않습니다.",
            code=ErrorCode.CIRCLE_NOT_FOUND,
        ).to_response(), None

    return None, circle


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
