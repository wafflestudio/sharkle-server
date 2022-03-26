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
    class Meta:
        model = Article
        fields = "__all__"
