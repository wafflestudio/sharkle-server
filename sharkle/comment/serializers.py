from rest_framework import serializers
from comment.models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {
            "article": {"required": True, "allow_null": False},
            "author": {"required": True, "allow_null": False},
        }


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "author_username",
            "content",
            "created_at",
            "reply_to",
            "is_deleted",
        ]

    def get_author_username(self, obj):
        return obj.author.username
