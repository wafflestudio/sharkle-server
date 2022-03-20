from rest_framework import viewsets, status
from rest_framework.response import Response

from board.BoardPermission import BoardPermission
from board.models import Board
from board.serializers import BoardSerializer

from circle.models import Circle, UserCircle_Member
from circle.permission import UserCirclePermission


# 1. check circle_id existence
# 2. if needed, circle member validate (create, update, destroy)
# 3. if request has board_id(pk), check board_id existence (retrieve, update, destroy)
# 4. if exist in 3, check circle_id in board model and url are the same
class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = (BoardPermission,)

    def create(self, request, **kwargs):
        data = request.data
        user = request.user
        circle_id = self.kwargs["circle_id"]
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if (err := self.circle_validate(user.id, circle_id, "생성")) is not None:
            return err
        data["circle"] = circle_id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    def list(self, request, **kwargs):
        circle_id = self.kwargs["circle_id"]
        user = request.user
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        member = UserCirclePermission(user.id, circle_id)
        if not member.is_member():  # 멤버가 아니면 비공게 게시판 숨기기
            boards = self.get_queryset().filter(circle=circle_id, is_private=False)
            return Response(self.get_serializer(boards, many=True).data)
        else:  # 멤버면 보든 게시판 공개
            boards = self.get_queryset().filter(circle=circle_id)
            return Response(self.get_serializer(boards, many=True).data)

    def retrieve(self, request, pk=None, **kwargs):
        circle_id = self.kwargs["circle_id"]
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if not self.get_queryset().filter(id=pk).exists():
            return Response(
                "id: " + str(pk) + "에 해당하는 게시판이 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        board = self.get_queryset().filter(id=pk).first()
        if board.circle.id != int(circle_id):
            return Response(
                "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
            )
        if board.is_private:
            user = request.user
            member = UserCirclePermission(user.id, circle_id)
            if not member.is_member():
                return Response(
                    "해당 게시판은 동아리원에게만 공개된 비밀 게시판입니다.", status=status.HTTP_400_BAD_REQUEST
                )

        serializer = self.get_serializer(board)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def update(self, request, pk=None, **kwargs):
        user = request.user
        circle_id = self.kwargs["circle_id"]
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if (err := self.circle_validate(user.id, circle_id, "수정")) is not None:
            return err

        if not self.get_queryset().filter(id=pk).exists():
            return Response(
                "id: " + str(pk) + "에 해당하는 게시판이 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        board = self.get_queryset().filter(id=pk).first()
        if board.circle.id != int(circle_id):
            return Response(
                "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(board, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(board, serializer.validated_data)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, **kwargs):
        user = request.user
        circle_id = self.kwargs["circle_id"]
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if (err := self.circle_validate(user.id, circle_id, "삭제")) is not None:
            return err

        if not self.get_queryset().filter(id=pk).exists():
            return Response(
                "id: " + str(pk) + "에 해당하는 게시판이 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        board = self.get_queryset().filter(id=pk).first()
        if board.circle.id != int(circle_id):
            return Response(
                "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
            )
        board.delete()
        return Response("id :" + str(pk) + " 게시판이 제거 되었습니다.", status=status.HTTP_200_OK)

    def circle_validate(self, user_id, circle_id, method):
        user_circle_permission = UserCirclePermission(user_id, circle_id)
        # 2. circle member validate
        if not user_circle_permission.is_member():
            return Response("해당 동아리에 가입되지 않았습니다.", status=status.HTTP_401_UNAUTHORIZED)
        # 3. circle manager validate
        if not user_circle_permission.is_manager():
            return Response(
                "동아리 게시판은 관리자만 " + method + "할 수 있습니다.",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return None
