from rest_framework import viewsets, status
from rest_framework.response import Response

from board.models import Board
from board.serializers import BoardSerializer

from circle.models import Circle, UserCircle_Member


class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def create(self, request, **kwargs):
        data = request.data

        if (response := self.circle_validate(request, kwargs)) is not None:
            return response

        serializer = BoardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardSerializer(board).data, status.HTTP_201_CREATED)

    def list(self, request, **kwargs):
        circle_id = self.kwargs["circle_id"]
        boards = self.get_queryset().filter(circle=circle_id)
        return Response(self.get_serializer(boards, many=True).data)

    def retrieve(self, request, pk=None, **kwargs):
        if self.get_queryset().filter(id=pk).exists():
            circle_id = self.kwargs["circle_id"]
            board = self.get_queryset().filter(id=pk).first()
            if board.circle != int(circle_id):
                return Response(
                    "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(board)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response("해당하는 게시판을 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, **kwargs):
        if self.get_queryset().filter(id=pk).exists():
            circle_id = self.kwargs["circle_id"]
            board = self.get_queryset().filter(id=pk).first()
            if board.circle != int(circle_id):
                return Response(
                    "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(board, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.update(board, validated_data=serializer.validated_data)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            return Response("해당하는 게시판을 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None, **kwargs):
        if (response := self.circle_validate(request, kwargs)) is not None:
            return response
        if self.get_queryset().filter(id=pk).exists():
            circle_id = self.kwargs["circle_id"]
            board = self.get_queryset().filter(id=pk).first()
            if board.circle != int(circle_id):
                return Response(
                    "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
                )
            board.delete()
            return Response(
                "id :" + str(board.id) + " 게시판이 제거 되었습니다.", status=status.HTTP_200_OK
            )
        else:
            return Response("해당하는 게시판을 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)

    def circle_validate(self, request, **kwargs):
        # 로그인 여부 검증
        user = request.user
        if user is None:
            return Response("로그인이 필요한 서비스입니다.", status=status.HTTP_401_UNAUTHORIZED)

        # url상의 circle id와 데이터 상의 circle id가 같은지 검증
        circle_id = self.kwargs["circle_id"]
        if circle_id != request.data["circle"]:
            return Response(
                "주소의 동아리 id와 데이터의 id가 다릅니다.", status=status.HTTP_400_BAD_REQUEST
            )

        # 동아리 존재 여부 검증
        if not Circle.objects.filter(id=circle_id).exists():
            return Response(
                "id: " + str(circle_id) + "에 해당하는 동아리가 존재하지 않습니다.",
                status=status.HTTP_404_NOT_FOUND,
            )

        member = UserCircle_Member.objects.filter(user_id=user.id, circle_id=circle_id)
        # 유저가 동아리 구성원인지 검증
        if not member.exists():
            return Response("해당 동아리에 가입되지 않았습니다.", status=status.HTTP_401_UNAUTHORIZED)
        # 유저가 동아리 관리자인지 검증
        if not member.first().is_manager:
            return Response(
                "동아리 게시판은 관리자만 생성할 수 있습니다.", status=status.HTTP_401_UNAUTHORIZED
            )
        return None
