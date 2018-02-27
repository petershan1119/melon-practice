import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.db import models

from artist.models import Artist
from crawler.utils.parsing import get_dict_from_dl
from utils.file import download


class AlbumManager(models.Manager):
    def update_or_create_from_melon(self, album_id):
        url = 'https://www.melon.com/album/detail.htm'
        params = {
            'albumId': album_id,
        }
        response = requests.get(url, params)
        soup = BeautifulSoup(response.text, 'lxml')
        info = soup.select_one('div.section_info')
        entry = info.select_one('div.entry')
        src = info.select_one('div.thumb img').get('src')

        title = entry.select_one('div.info > .song_name').contents[2].strip()
        img_cover = re.search(r'(.*?)/melon/quality.*', src).group(1)
        # if re.findall('http.*?\.jpg', url_img_cover):
        #     url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
        # else:
        #     url_img_cover = "http://cdnimg.melon.co.kr/resource/image/web/default/noAlbum_500_160727.jpg"

        meta_dict = get_dict_from_dl(entry.select_one('div.meta dl'))

        # response = requests.get(url_img_cover)
        # binary_data = response.content
        # temp_file = BytesIO()
        # temp_file.write(binary_data)
        # # temp_file.seek(0)

        try:
            release_date = datetime.strptime(meta_dict['발매일'], '%Y.%m.%d')
        except ValueError:
            try:
                release_date = datetime.strptime(meta_dict['발매일'], '%Y.%m')
            except ValueError:
                try:
                    release_date = datetime.strptime(meta_dict['발매일'], '%Y')
                except ValueError:
                    release_date = None

        album, album_created = Album.objects.update_or_create(
            melon_id=album_id,
            defaults={
                'title': title,
                'release_date': release_date,
            }
        )
        # file_name = Path(url_img_cover).name
        file_name, temp_file = download(img_cover, album_id)
        album.img_cover.save(file_name, File(temp_file))
        return album, album_created


class Album(models.Model):
    melon_id = models.CharField(
        '멜론 Album ID',
        max_length=20,
        blank=True,
        null=True,
    )
    title = models.CharField(
        '앨범명',
        max_length=100,
    )
    img_cover = models.ImageField(
        '커버 이미지',
        upload_to='album',
        blank=True,
    )
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='AlbumLike',
        related_name='like_albums',
        blank=True,
    )
    # artists = models.ManyToManyField(
    #     Artist,
    #     verbose_name='아티스트 목록',
    # )
    release_date = models.DateField(blank=True, null=True)

    objects = AlbumManager()

    @property
    def genre(self):
        return ', '.join(self.song_set.values_list('genre', flat=True)).distinct()

    # def __str__(self):
    #     return '{title} [{artists}]'.format(
    #         title=self.title,
    #         artists=', '.join(self.artists.values_list('name', flat=True)),
    #     )
    def __str__(self):
        return self.title

    def toggle_like_user(self, user):
        like, like_created = self.like_user_info_list.get_or_create(user=user)
        if not like_created:
            like.delete()
        return like_created


class AlbumLike(models.Model):
    album = models.ForeignKey(Album, related_name='like_user_info_list', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='like_album_info_list', on_delete=models.CASCADE)

    create_date = models.DateTimeField(
        auto_now_add=True,
    )
    class Meta:
        unique_together = (
            ('album', 'user'),
        )

    def __str__(self):
        return 'AlbumLike (User: {user}, Album: {album}, Created: {create_date})'.format(
            user=self.user.username,
            album=self.album.title,
            create_date=datetime.strptime(self.create_date, '%Y.%m.%d'),
        )