from rest_framework import serializers
from board.models import Board


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ("id", "name", "type", "circle", "is_private", "created_at", "updated_at")
