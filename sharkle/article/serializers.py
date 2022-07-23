from rest_framework import serializers
from article.models import Article


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"
        extra_kwargs = {
            "board": {"required": True, "allow_null": False},
            "author": {"required": True, "allow_null": False},
        }


class ArticleSerializer(serializers.ModelSerializer):
    author_id = serializers.SerializerMethodField()
    author_username = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "author_id",
            "author_username",
            "is_private",
            "title",
            "content",
            "created_at",
            "updated_at",
        )

    def get_author_id(self, obj):
        return obj.author.id

    def get_author_username(self, obj):
        return obj.author.username
