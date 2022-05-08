from circle.models import UserCircle_Member


class UserCirclePermission:
    def __init__(self, user_id, circle_id):
        self.member = UserCircle_Member.objects.filter(
            user_id=user_id, circle_id=circle_id
        )

    def is_member(self):
        return self.member.exists()

    def is_manager(self):  # Q. self.member.exists() and self.member.first().is_manager?
        return self.member.first().is_manager
