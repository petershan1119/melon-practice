from django.db import models

from artist.models import Artist


class Album(models.Model):
    title = models.CharField(
        '앨범명',
        max_length=100,
    )
    img_cover = models.ImageField(
        '커버 이미지',
        upload_to='album',
        blank=True,
    )
    artists = models.ManyToManyField(
        Artist,
        verbose_name='아티스트 목록',
    )
    release_date = models.DateField()

    def __str__(self):
        return '{title} [{artists}]'.format(
            title=self.title,
            artists=', '.join(self.artists.values_list('name', flat=True)),
        )