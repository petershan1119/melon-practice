import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup, NavigableString
from django.core.files import File
from django.db import models

from album.models import Album
from artist.models import Artist
from utils.file import download


class SongManager(models.Manager):
    def update_or_create_from_song_id(self, song_id):
        """
        Song의 Album정보도 가져와서 AlbumManager.update_or_create_from_melon도 실행
            -> Album의 커버이미지도 저장
        """
        url_song = 'https://www.melon.com/song/detail.htm'
        params_song = {
            'songId': song_id,
        }
        response_song = requests.get(url_song, params_song)
        soup_song = BeautifulSoup(response_song.text, 'lxml')

        thumb_entry = soup_song.find('div', class_='thumb')
        url_img_cover = thumb_entry.find('img').get('src')
        if re.findall('http.*?\.jpg', url_img_cover):
            url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
        else:
            url_img_cover = "http://cdnimg.melon.co.kr/resource/image/web/default/noAlbum_500_160727.jpg"

        div_entry = soup_song.find('div', class_='entry')

        title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()

        artist = div_entry.find('div', class_='artist').get_text(strip=True)
        artist_id_a = div_entry.select_one('div.artist a').get('href')
        artist_id = re.findall(r'\(\'(.*?)\'\)', artist_id_a)[0]
        # 앨범, 발매일, 장르...에 대한 Description list
        dl = div_entry.find('div', class_='meta').find('dl')
        # isinstance(인스턴스, 클래스(타입))
        # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
        items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
        it = iter(items)
        description_dict = dict(zip(it, it))

        album = description_dict.get('앨범')
        album_id_a = str(dl.select_one('a'))
        album_id = re.findall(r'\(\'(.*?)\'\)', album_id_a)[0]
        # release_date = description_dict.get('발매일')
        genre = description_dict.get('장르')

        div_lyrics = soup_song.find('div', id='d_video_summary')

        lyrics_list = []
        if div_lyrics:
            for item in div_lyrics:
                if item.name == 'br':
                    lyrics_list.append('\n')
                elif type(item) is NavigableString:
                    lyrics_list.append(item.strip())
            lyrics = ''.join(lyrics_list)
        else:
            lyrics = '가사가 없습니다'

        # # if Album.objects.get(title=album):
        # # url_img_cover는 이미지의 URL
        # response = requests.get(url_img_cover)
        # # requests에 GET요청을 보낸 결과의 Binary data
        # binary_data = response.content
        # # 파일처럼 취급되는 메모리 객체 temp_file를 생성
        # temp_file = BytesIO()
        # # temp_file에 이진데이터를 기록
        # temp_file.write(binary_data)
        # # 파일객체의 포인터를 시작부분으로 되돌림
        # # temp_file.seek(0)

        # artist = ArtistData(artist_id)
        # artist.get_detail()
        #
        # name = artist.name
        # url_img_cover = artist.url_img_cover
        # url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
        # real_name = artist.personal_information.get('본명', '')
        # nationality = artist.personal_information.get('국적', '')
        # birth_date_str = artist.personal_information.get('생일', '')
        # if not birth_date_str or len(birth_date_str) <= 9:
        #     birth_date_str = '1900.01.01'
        # constellation = artist.personal_information.get('별자리', '')
        # blood_type = artist.personal_information.get('혈액형', '')
        #
        # for short, full in Artist.CHOICES_BLOOD_TYPE:
        #     if blood_type.strip() == full:
        #         blood_type = short
        #         break
        #     else:
        #         blood_type = Artist.BLOOD_TYPE_OTHER
        #
        # response = requests.get(url_img_cover)
        # binary_data = response.content
        # temp_file = BytesIO()
        # temp_file.write(binary_data)
        # temp_file.seek(0)
        #
        # artist, _ = Artist.objects.update_or_create(
        #     melon_id=artist_id,
        #     defaults={
        #         'name': name,
        #         'real_name': real_name,
        #         'nationality': nationality,
        #         'birth_date': datetime.strptime(birth_date_str, '%Y.%m.%d'),
        #         'constellation': constellation,
        #         'blood_type': blood_type,
        #     }
        # )
        #
        # file_name = Path(url_img_cover).name
        # artist.img_profile.save(file_name, File(temp_file))
        #
        album, _ = Album.objects.update_or_create_from_melon(album_id)
        # song.album.add(album)

        song, song_created = Song.objects.update_or_create(
            song_id=song_id,
            defaults={
                # 'album': Album.objects.get(title=album),
                'title': title,
                'genre': genre,
                'lyrics': lyrics,
                'album': album,
            }
        )

        artist, _ = Artist.objects.update_or_create_from_melon(artist_id)
        song.artists.add(artist)

        # file_name = Path(url_img_cover).name
        file_name, temp_file = download(url_img_cover, song_id)
        song.img_cover.save(file_name, File(temp_file))
        return song, song_created


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

    objects = SongManager()

    # @property
    # def artists(self):
    #     return self.album.artists.all()

    @property
    def release_date(self):
        return self.album.release_date

    @property
    def formatted_release_date(self):
        return self.release_date.strftime('%Y.%m.%d')

    # def __str__(self):
    #     return '{artists} - {title} ({album})'.format(
    #         artists=','.join(self.album.artists.values_list('name', flat=True)),
    #         title=self.title,
    #         album=self.album.title,
    #     )

    def __str__(self):
        return self.title