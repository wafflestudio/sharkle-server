from rest_framework import viewsets, status
from rest_framework.response import Response

from board.models import Board
from board.serializers import BoardSerializer


# Create your views here.


class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def create(self, request, **kwargs):
        data = request.data
        user = request.user
        # 유저 권한 인증
        circle_id = self.kwargs["circle_id"]
        if circle_id != request.data["circle"]:
            return Response(
                "주소의 동아리 id와 데이터의 id가 다릅니다.", status=status.HTTP_400_BAD_REQUEST
            )
        # 동아리 존재 여부 검증
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
