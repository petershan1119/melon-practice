from django.contrib.auth.models import AbstractUser
from django.db import models

from album.models import AlbumLike
from artist.models import ArtistLike
from song.models import SongLike


class User(AbstractUser):

    img_profile = models.ImageField(
        upload_to='user',
        blank=True,
    )

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


    def toggle_like_album(self, album):
        query = AlbumLike.objects.filter(album=album, user=self)
        if query.exists():
            query.delete()
            return False
        else:
            AlbumLike.objects.create(album=album, user=self)
            return True

        like, like_created = self.like_album_info_list.get_or_create(album=album)
        if not like_created:
            like.delete()
        return like_created

    def toggle_like_song(self, song):
        query = SongLike.objects.filter(song=song, user=self)
        if query.exists():
            query.delete()
            return False
        else:
            SongLike.objects.create(song=song, user=self)
            return True

        like, like_created = self.like_song_info_list.get_or_create(song=song)
        if not like_created:
            like.delete()
        return like_created