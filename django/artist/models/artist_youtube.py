from django.db import models


__all__ = (
    'ArtistYouTube',
)

class ArtistYouTube(models.Model):
    youtube_id = models.CharField('YouTube ID', primary_key=True, max_length=20)
    title = models.CharField('제목', max_length=200)