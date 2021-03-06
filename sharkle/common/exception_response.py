from enum import Enum

from rest_framework.response import Response


class ExceptionResponse:
    status = None
    detail = ""
    code = 0

    def __init__(self, status, detail, code):
        self.status = status
        self.detail = detail
        self.code = code

    def to_response(self):
        return Response(
            status=self.status,
            data={
                "status": self.status,
                "detail": self.detail,
                "code": self.code.value,
            },
        )


class ErrorCode(Enum):
    INVALID_REQUEST = 0  # NOT used
    BOARD_NOT_IN_CIRCLE = 1
    PASSWORD_FORMAT_INVALID = 2

    NOT_ALLOWED = 3000  # NOT used
    NOT_MEMBER = 3001
    NOT_MANAGER = 3002
    NOT_AUTHOR_OR_MANAGER = 3003
    ANONYMOUS_USER = 3004

    DATA_NOT_FOUND = 4000  # NOT used
    CIRCLE_NOT_FOUND = 4001
    BOARD_NOT_FOUND = 4002
    USER_NOT_FOUND = 4003
    RECRUITMENT_NOT_FOUND = 4004
    SCHEDULE_NOT_FOUND = 4005
    ARTICLE_NOT_FOUND = 4006
    COMMENT_NOT_FOUND = 4007

    CONFLICT = 9000  # NOT used
    PAGINATION_FAULT = 9001
    DATABASE_ERROR = 9002

    SERVER_ERROR = 10000  # NOT used
