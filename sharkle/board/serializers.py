from rest_framework import serializers
from board.models import Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        # num_of_articles ...
        model = Board
        fields = ("id", "name", "created_at", "updated_at")
