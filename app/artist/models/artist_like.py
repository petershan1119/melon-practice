from datetime import datetime
from django.conf import settings
from django.db import models

from .artist import Artist


__all__ = (
    "ArtistLike",
)


class ArtistLike(models.Model):
    # Artist와 User(members.User)와의 관계를 나타내는 중계모델
    artist = models.ForeignKey(Artist, related_name='like_user_info_list', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='like_artist_info_list', on_delete=models.CASCADE)

    create_date = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = (
            ('artist', 'user'),
        )

    def __str__(self):
        return 'ArtistLike (User: {user}, Artist: {artist}, Created: {create_date})'.format(
            user=self.user.username,
            artist=self.artist.name,
            create_date=datetime.strftime(self.create_date, '%Y.%m.%d'),
        )