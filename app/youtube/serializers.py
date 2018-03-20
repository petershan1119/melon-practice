from rest_framework import serializers

from .models import Youtube

__all__ = (
    'YoutubeSerializer',
)


class YoutubeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Youtube
        # fields = '__all__'
        fields = '__all__'