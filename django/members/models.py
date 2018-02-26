from django.contrib.auth.models import AbstractUser
from django.db import models

from artist.models import ArtistLike


class User(AbstractUser):

    def toggle_like_artist(self, artist):
        """
        이 User의 특정 Artist를 연결하는 중개모델인 ArtistList인스턴스를
            없을 경우 생성, 있으면 삭제하는 메서드
        """
        query = ArtistLike.objects.filter(artist=artist, user=self)
        if query.exists():
            query.delete()
            return False
        else:
            ArtistLike.objects.create(artist=artist, user=self)
            return True

        like, like_created = self.like_artist_info_list.get_or_create(artist=artist)
        if not like_created:
            like.delete()
        return like_created