from rest_framework import serializers

from .models import Hashtag

class HashtagSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        model = Hashtag
        fields = ['id', 'name']
        #extra_fields = ['problems']