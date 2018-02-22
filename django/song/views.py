import re
from io import BytesIO
from pathlib import Path

import requests
from typing import NamedTuple
from bs4 import BeautifulSoup, NavigableString
from django.core.files import File
from django.db.models import Q
from django.shortcuts import render, redirect

from album.models import Album
from .models import Song


def song_list(request):
    songs = Song.objects.all()
    context = {
        'songs': songs,
    }
    return render(request, 'song/song_list.html', context)

def song_search(request):
    # context = {}
    # if request.method == "POST":
    #     keyword = request.POST['keyword'].strip()
    #
    #     if keyword:
    #         songs = Song.objects.filter(
    #             Q(album__title__contains=keyword)|
    #             Q(album__artists__name__contains=keyword)|
    #             Q(title__contains=keyword)
    #         ).distinct()
    #         context['songs'] = songs
    #
    #         songs_from_artists = Song.objects.filter(
    #             album__artists__name__contains=keyword,
    #         )
    #         context['songs_from_artists'] = songs_from_artists
    #
    #         songs_from_albums = Song.objects.filter(
    #             album__title__contains=keyword,
    #         )
    #         context['songs_from_albums'] = songs_from_albums
    #
    #         songs_from_title = Song.objects.filter(
    #             title__contains=keyword,
    #         )
    #         context['songs_from_title'] = songs_from_title

    context = {
        'song_infos': [],
    }
    keyword = request.GET.get('keyword')

    if keyword:
        class SongInfo(NamedTuple):
            type: str
            q: Q

        song_infos = (
            SongInfo(
                type='아티스트명',
                q=Q(album__artists__name__contains=keyword)
            ),
            SongInfo(
                type='앨범명',
                q=Q(album__title__contains=keyword)
            ),
            SongInfo(
                type='노래제목',
                q=Q(title__contains=keyword)
            ),
        )
        for type, q in song_infos:
            context['song_infos'].append({
                'type': type,
                'songs': Song.objects.filter(q),

            })
    return render(request, 'song/song_search.html', context)


def song_search_from_melon(request):
    context = {}
    keyword = request.GET.get('keyword')

    if keyword:
        song_info_list = []
        url = 'https://www.melon.com/search/song/index.htm'
        params = {
            'q': keyword,
            'section': 'song',
        }
        response = requests.get(url, params)
        soup = BeautifulSoup(response.text, 'lxml')
        tr_list = soup.select('form#frm_defaultList table > tbody > tr')

        for tr in tr_list:
            song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
            if tr.select_one('td:nth-of-type(3) a.fc_gray'):
                title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
            else:
                title = '타이틀이 없습니다'
            artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(strip=True)
            album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

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
            if div_entry.select_one('div.artist a'):
                artist_id_a = div_entry.select_one('div.artist a').get('href')
                artist_id = re.findall(r'\(\'(.*?)\'\)', artist_id_a)[0]
            else:
                artist_id = "000000"
            # 앨범, 발매일, 장르...에 대한 Description list
            dl = div_entry.find('div', class_='meta').find('dl')
            # isinstance(인스턴스, 클래스(타입))
            # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
            items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
            it = iter(items)
            description_dict = dict(zip(it, it))

            album = description_dict.get('앨범')
            album_id_a = str(dl.select_one('a'))
            if album_id_a:
                album_id = re.findall(r'\(\'(.*?)\'\)', album_id_a)[0]
            else:
                album_id = "000000"
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

            song_info_list.append({
                'song_id': song_id,
                'url_img_cover': url_img_cover,
                'artist': artist,
                'artist_id': artist_id,
                'album': album,
                'album_id': album_id,
                'title': title,
                'genre': genre,
                'lyrics': lyrics,
            })
        context['song_info_list'] = song_info_list
    return render(request, 'song/song_search_from_melon.html', context)


def song_add_from_melon(request):
    # 패키지 분할 (artist랑 똑같은 형태로)
    # artist_add_from_melon과 같은 기능을 함
    #   song_search_from_melon도 구현
    #       -> 이 안에 'DB에 추가'하는 Form구현
    if request.method == "POST":
        song_id = request.POST['song_id']

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

        if Album.objects.get(title=album):
            response = requests.get(url_img_cover)
            binary_data = response.content
            temp_file = BytesIO()
            temp_file.write(binary_data)
            temp_file.seek(0)

            song, _ = Song.objects.update_or_create(
                song_id=song_id,
                defaults={
                    'album': Album.objects.get(title=album),
                    'title': title,
                    'genre': genre,
                    'lyrics': lyrics,
                }
            )

            file_name = Path(url_img_cover).name
            song.img_cover.save(file_name, File(temp_file))
    return redirect('song:song-list')