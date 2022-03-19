from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from article.models import Article
from article.serializers import ArticleSerializer
from rest_framework.response import Response

# Create your views here.


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()  # .... not appropriate?
    serializer_class = ArticleSerializer
    permission_classes = (permissions.IsAuthenticated,)  # TODO

    # TODO POST /circle/{id}/board/{id}/article/
    def create(self, request, circle_id, board_id):  # TODO request // id.. how kwargs?
        user = request.user
        data = request.data.copy()
        data["board"] = board_id
        data["author"] = user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    # TODO GET /circle/{id}/board/{id}/article/
    def list(self, request, circle_id, board_id):
        articles = self.get_queryset().filter(board=board_id)
        return Response(self.get_serializer(articles, many=True).data)

    # TODO GET /circle/{id}/board/{id}/article/{id}/
    def retrieve(self, request, circle_id, board_id, pk=None):
        article = self.get_queryset().filter(id=pk).first()
        return Response(self.get_serializer(article).data)

    # TODO PUT /circle/{id}/board/{id}/article/{id}/
    def update(self, request, circle_id, board_id, pk=None):
        article = self.get_queryset().filter(id=pk).first()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # TODO DELETE /circle/{id}/board/{id}/article/{id}/
    def destroy(self, request, circle_id, board_id, pk):
        article = self.get_queryset().filter(id=pk).first()
        article.delete()
        return Response("id :" + str(pk) + " 게시글이 제거 되었습니다.", status=status.HTTP_200_OK)
