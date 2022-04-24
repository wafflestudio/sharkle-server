from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from comment.models import Comment
from comment.serializers import CommentSerializer, CommentCreateSerializer
from rest_framework.response import Response
from circle.permission import UserCirclePermission

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

    # GET article/{id}/comment/ TODO nested ??
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
        user = request.user
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "댓글이 존재하지 않습니다."},
            )
        circle_permission = UserCirclePermission(
            user.id, comment.article.board.circle.id
        )
        if comment.author != user and not (
            circle_permission.is_member() and circle_permission.is_manager()
        ):
            return Response(
                "댓글 작성자 또는 동아리 관리자만 댓글을 수정할 수 있습니다.",
                status=status.HTTP_401_UNAUTHORIZED,
            )
        serializer = self.get_serializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE article/{id}/comment/{id}/ TODO question
    def destroy(self, request, article_id, pk=None):
        user = request.user
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error": "wrong_id", "detail": "댓글이 존재하지 않습니다."},
            )
        circle_permission = UserCirclePermission(
            user.id, comment.article.board.circle.id
        )
        if comment.author != user and not (
            circle_permission.is_member() and circle_permission.is_manager()
        ):
            return Response(
                "댓글 작성자 또는 동아리 관리자만 댓글을 삭제할 수 있습니다.",
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not comment.replies.exists():
            comment.delete()
        else:  # 삭제하려는 댓글에 달린 대댓글이 존재하는 경우
            comment.is_delete = True
            comment.content = "삭제된 댓글입니다."
            comment.author = None
            comment.save()
        return Response("id :" + str(pk) + " 댓글이 제거 되었습니다.", status=status.HTTP_200_OK)
