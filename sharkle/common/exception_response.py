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
            status=self.status, data={"detail": self.message, "code": self.code}
        )


class ErrorCode(Enum):
    INVALID_REQUEST = 0  # NOT used
    BOARD_NOT_IN_CIRCLE = 1

    NOT_ALLOWED = 3000  # NOT used
    NOT_MEMBER = 3001
    NOT_MANAGER = 3002

    DATA_NOT_FOUND = 4000  # NOT used
    CIRCLE_NOT_FOUND = 4001
    BOARD_NOT_FOUND = 4001

    CONFLICT = 9000  # NOT used

    SERVER_ERROR = 10000  # NOT used
