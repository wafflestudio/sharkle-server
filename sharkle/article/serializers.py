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
    comments_counts = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "author_id",
            "author_username",
            "is_private",
            "title",
            "content",
            "view",
            "comments_counts",
            "created_at",
            "updated_at",
        )

    def get_author_id(self, obj):
        return obj.author.id

    def get_author_username(self, obj):
        return obj.author.username

    def get_comments_counts(self, obj):
        print(type(obj.comments))
        return obj.comments.count()
