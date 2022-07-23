from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from article.models import Article
from article.serializers import ArticleSerializer, ArticleCreateSerializer
from rest_framework.response import Response
from common.exception_response import ExceptionResponse, ErrorCode

# Create your views here.


class ArticleViewSet(viewsets.GenericViewSet):
    queryset = Article.objects.all()  # .... not appropriate?
    serializer_class = ArticleSerializer
    permission_classes = (permissions.AllowAny,)  # TODO

    # POST /circle/{id}/board/{id}/article/
    def create(self, request, circle_id, board_id):  # TODO request // id.. how kwargs?
        user = request.user
        data = request.data.copy()
        data["board"] = board_id
        data["author"] = user.id
        serializer = ArticleCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    # GET /circle/{id}/board/{id}/article/ TODO pagination
    def list(self, request, circle_id, board_id):
        articles = self.get_queryset().filter(board=board_id)
        data = self.get_serializer(articles, many=True).data
        return Response(
            {"articles": data, "count": articles.count()}, status=status.HTTP_200_OK
        )

    # GET /circle/{id}/board/{id}/article/{id}/
    def retrieve(self, request, circle_id, board_id, pk=None):
        if not (article := Article.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 게시물이 존재하지 않습니다.",
                code=ErrorCode.ARTICLE_NOT_FOUND,
            ).to_response()
        article.view = article.view + 1
        article.save()
        return Response(self.get_serializer(article).data)

    # PUT /circle/{id}/board/{id}/article/{id}/
    def update(self, request, circle_id, board_id, pk=None):
        if not (article := Article.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 게시물이 존재하지 않습니다.",
                code=ErrorCode.ARTICLE_NOT_FOUND,
            ).to_response()
        serializer = self.get_serializer(article, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE /circle/{id}/board/{id}/article/{id}/
    def destroy(self, request, circle_id, board_id, pk):
        if not (article := Article.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 게시물이 존재하지 않습니다.",
                code=ErrorCode.ARTICLE_NOT_FOUND,
            ).to_response()
        article.delete()
        return Response("id :" + str(pk) + " 게시글이 제거 되었습니다.", status=status.HTTP_200_OK)


## possible to modify main?
