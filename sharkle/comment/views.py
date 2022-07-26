from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from comment.models import Comment
from comment.serializers import CommentSerializer, CommentCreateSerializer
from rest_framework.response import Response
from user_circle.permission import UserCirclePermission
from common.exception_response import ExceptionResponse, ErrorCode

# Create your views here.
class CommentViewSet(viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticated,)  # TODO

    def dfs_comment(self, article_id):
        comments = self.get_queryset().filter(article=article_id)

        parent_to_child = {}

        for comment in comments:
            parent_to_child[comment] = []

        for child in comments:
            parent = child.reply_to
            if parent:
                parent_to_child[parent].append(child)

        sequence = []

        for comment in self.get_queryset().filter(article=article_id, reply_to=None):
            stack_comment = [comment]
            stack_depth = [0]

            while len(stack_depth):
                comment_ = stack_comment.pop()
                depth_ = stack_depth.pop()

                comment_.depth = depth_

                sequence.append(comment_)

                stack_comment = stack_comment + parent_to_child[comment_][-1::-1]
                stack_depth = stack_depth + [depth_ + 1] * len(parent_to_child[comment_])

        return sequence

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
        comments = self.dfs_comment(article_id)
        return Response(self.get_serializer(comments, many=True).data)

    # GET article/{id}/comment/{id}/
    def retrieve(self, request, article_id, pk=None):
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 댓글이 존재하지 않습니다.",
                code=ErrorCode.COMMENT_NOT_FOUND,
            ).to_response()
        return Response(self.get_serializer(comment).data)

    # PUT article/{id}/comment/{id}/
    def update(self, request, article_id, pk=None):
        user = request.user
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 댓글이 존재하지 않습니다.",
                code=ErrorCode.COMMENT_NOT_FOUND,
            ).to_response()
        circle_permission = UserCirclePermission(
            user.id, comment.article.board.circle.id
        )
        if comment.author != user and not (
            circle_permission.is_member() and circle_permission.is_manager()
        ):
            return ExceptionResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                detail="댓글 작성자 또는 동아리 관리자만 댓글을 수정할 수 있습니다.",
                code=ErrorCode.NOT_AUTHOR_OR_MANAGER,
            ).to_response()
        serializer = self.get_serializer(comment, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    # DELETE article/{id}/comment/{id}/ TODO question
    def destroy(self, request, article_id, pk=None):
        user = request.user
        if not (comment := Comment.objects.get_or_none(id=pk)):
            return ExceptionResponse(
                status=status.HTTP_404_NOT_FOUND,
                detail="id: " + str(pk) + "에 해당하는 댓글이 존재하지 않습니다.",
                code=ErrorCode.COMMENT_NOT_FOUND,
            ).to_response()
        circle_permission = UserCirclePermission(
            user.id, comment.article.board.circle.id
        )
        if comment.author != user and not (
            circle_permission.is_member() and circle_permission.is_manager()
        ):
            return ExceptionResponse(
                status=status.HTTP_401_UNAUTHORIZED,
                detail="댓글 작성자 또는 동아리 관리자만 댓글을 수정할 수 있습니다.",
                code=ErrorCode.NOT_AUTHOR_OR_MANAGER,
            ).to_response()
        if not comment.replies.exists():
            comment.delete()
        else:  # 삭제하려는 댓글에 달린 대댓글이 존재하는 경우
            comment.is_delete = True
            comment.content = "삭제된 댓글입니다."
            comment.author = None
            comment.save()
        return Response("id :" + str(pk) + " 댓글이 제거 되었습니다.", status=status.HTTP_200_OK)
