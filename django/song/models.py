from django.db import models

from album.models import Album
from artist.models import Artist


class Song(models.Model):
    album = models.ForeignKey(
        Album,
        verbose_name='앨범',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    song_id = models.CharField(
        '멜론 Song ID',
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )
    artists = models.ManyToManyField(
        Artist,
        verbose_name='아티스트 목록',
        blank=True,
    )
    img_cover = models.ImageField(
        '커버 이미지',
        upload_to='song',
        blank=True,
    )
    title = models.CharField(
        '곡 제목',
        max_length=100,
    )
    genre = models.CharField(
        '장르',
        max_length=100,
    )
    lyrics = models.TextField(
        '가사',
        blank=True,
    )

    # @property
    # def artists(self):
    #     return self.album.artists.all()

    @property
    def release_date(self):
        return self.album.release_date

    @property
    def formatted_release_date(self):
        return self.release_date.strftime('%Y.%m.%d')

    def __str__(self):
        return '{artists} - {title} ({album})'.format(
            artists=','.join(self.album.artists.values_list('name', flat=True)),
            title=self.title,
            album=self.album.title,
        )