from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from comment.models import Comment
from comment.serializers import CommentSerializer, CommentCreateSerializer
from rest_framework.response import Response

# Create your views here.
class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)  # TODO

    # POST article/{id}/comment/?reply_to=~~  TODO nested
    def create(self, request, article_id):
        reply_to = request.query_params.get("reply_to", None)
        user = request.user
        data = request.data.copy()
        data["article"] = article_id
        data["author"] = user.id
        data["reply_to"] = reply_to

        serializer = CommentCreateSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_201_CREATED)

    # GET article/{id}/comment/ TODO nested
    def list(self, request, article_id):
        comments = self.get_queryset().filter(article=article_id)
        return Response(self.get_serializer(comments, many=True).data)

    # GET article/{id}/comment/{id}/
    def retrieve(self, request, article_id, pk=None):
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "댓글이 존재하지 않습니다."},
            )
        return Response(self.get_serializer(comment).data)

    # PUT article/{id}/comment/{id}/
    def update(self, request, article_id, pk=None):
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "댓글이 존재하지 않습니다."},
            )
        serializer = self.get_serializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE article/{id}/comment/{id}/
    def destroy(self, request, article_id, pk=None):
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "댓글이 존재하지 않습니다."},
            )
        comment.delete()
        return Response("id :" + str(pk) + " 댓글이 제거 되었습니다.", status=status.HTTP_200_OK)
