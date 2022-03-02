from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from board.models import Board
from board.serializers import BoardSerializer


# Create your views here.


class BoardViewSet(viewsets.GenericViewSet):
    queryset = Board.objects.all()

    def create(self, request, circle_id):
        data = request.data
        user = request.user
        # 유저 권한 인증
        serializer = BoardSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        board = serializer.save()

        return Response(BoardSerializer(board).data, status.HTTP_201_CREATED)

    def list(self, request, circle_id):
        boards = self.getqueryset().filter(circle=circle_id)
        return Response(self.get_serializer(boards, many=True).data)

    def retrieve(self, request, circle_id, pk=None):
        if self.get_queryset().filter(id=pk).exists():
            board = self.get_queryset().get(id=pk)
            if board.circle != circle_id:
                return Response(
                    "게시판이 해당 동아리에 존재하지 않습니다.", status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response("해당하는 개시판을 찾을 수 없습니다.", status=status.HTTP_404_NOT_FOUND)
