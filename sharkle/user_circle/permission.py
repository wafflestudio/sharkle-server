from user_circle.models import UserCircleMember, Membership


class UserCirclePermission:
    def __init__(self, user_id, circle_id):
        self.member = UserCircleMember.objects.filter(
            user_id=user_id, circle_id=circle_id
        )

    def is_member(self):
        return self.member.membership >= Membership.일반

    def is_manager(self):  # Q. self.member.exists() and self.member.first().is_manager?
        return self.member.membership >= Membership.관리자

    def is_applicant(self):
        return self.member.membership == Membership.가입신청
