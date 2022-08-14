from rest_framework import serializers
from comment.models import Comment
from user.serializers import UserViewSerializer


class CommentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"
        extra_kwargs = {
            "article": {"required": True, "allow_null": False},
            "author": {"required": True, "allow_null": False},
        }


class CommentSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()
    author_info = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = "__all__"

    def get_author_id(self, obj):
        return obj.author.id

    def get_author_username(self, obj):
        return obj.author.username

    def get_author_info(self, obj):
        return UserViewSerializer(obj.author).data