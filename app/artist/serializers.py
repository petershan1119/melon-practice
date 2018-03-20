from rest_framework import serializers

from members.serializers import UserSerializer
from youtube.serializers import YoutubeSerializer
from .models import Artist


class ArtistSerializer(serializers.ModelSerializer):
    like_users = UserSerializer(many=True, read_only=True)
    youtube_links = YoutubeSerializer(many=True, read_only=True)
    class Meta:
        model = Artist
        fields = '__all__'
        # fields = (
        #     'pk',
        #     'like_users',
        #     'youtube_link',
        # )
        # # fields = (
        # #     'pk',
        # #     'like_users',
        # # )