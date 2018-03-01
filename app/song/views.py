import re
from io import BytesIO
from pathlib import Path

import requests
from typing import NamedTuple
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from django.core.files import File
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from album.models import Album
from artist.models import Artist
from crawler.artist import ArtistData
from song.forms import SongForm
from .models import Song


def song_list(request):
    songs = Song.objects.all()
    context = {
        'songs': songs,
    }
    return render(request, 'song/song_list.html', context)


def song_add(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('song:song-list')
    else:
        form = SongForm()

    context = {
        'song_form': form,
    }
    return render(request, 'song/song_add.html', context)

def song_edit(request, song_pk):
    song = get_object_or_404(Song, pk=song_pk)
    if request.method == "POST":
        form = SongForm(request.POST, request.FILES, instance=song)
        if form.is_valid():
            form.save()
            return redirect('song:song-edit')
    else:
        form = SongForm(instance=song)
    context = {
        'song_form': form,
    }
    return render(request, 'song/song_edit.html', context)

def song_detail(request, song_pk):
    song = get_object_or_404(Song, pk=song_pk)
    context = {
        'song': song,
    }
    return render(request, 'song/song_detail.html', context)

def song_like_toggle(request, song_pk):
    song = Song.objects.get(pk=song_pk)
    if request.method == "POST":
        song.toggle_like_user(user=request.user)
        next_path = request.POST.get('next-path', 'song:song-list')
        return redirect(next_path)


def song_search(request):
    """
    사용할 URL: song/search/
    사용할 Template: templates/song/song_search.html
        form안에
            input한개, button한개 배치
    1. song/urls.py에 URL작성
    2. templates/song/song_search.html작성
        {% extends %} 사용할 것
        form배치 후 method는 POST, {% csrf_token %}배치
    3. 이 함수에서 return render(...)
        *아직 context는 사용하지 않음
    - GET, POST분기
    1. input의 name을 keyword로 지정
    2. 이 함수를 request.method가 'GET'일 때와 'POST'일 때로 분기
    3. request.method가 'POST'일 때
        request.POST dict의 'keyword'키에 해당하는 값을
        HttpResponse로 출력
    4. request.method가 'GET'일 때
        이전에 하던 템플릿 출력을 유지
    - Query filter로 검색하기
    1. keyword가 자신의 'title'에 포함되는 Song쿼리셋 생성
    2.  위 쿼리셋을 'songs'변수에 할당
    3. context dict를 만들고 'songs'키에 songs변수를 할당
    4. render의 3번째 인수로 context를 전달
    5. template에 전달된 'songs'를 출력
        song_search.html을 그대로 사용
    :param request:
    :return:
    """
    context = {
        'song_infos': [],
    }
    keyword = request.GET.get('keyword')

    if keyword:
        class SongInfo(NamedTuple):
            type: str
            q: Q

        song_infos = (
            # SongInfo(
            #     type='아티스트명',
            #     q=Q(album__artists__name__contains=keyword)),
            SongInfo(
                type='앨범명',
                q=Q(album__title__contains=keyword)),
            SongInfo(
                type='노래제목',
                q=Q(title__contains=keyword)),
        )
        for type, q in song_infos:
            context['song_infos'].append({
                'type': type,
                'songs': Song.objects.filter(q),
            })
    return render(request, 'song/song_search.html', context)


# def song_search_from_melon(request):
#     context = {}
#     keyword = request.GET.get('keyword')
#
#     if keyword:
#         song_info_list = []
#         url = 'https://www.melon.com/search/song/index.htm'
#         params = {
#             'q': keyword,
#             'section': 'song',
#         }
#         response = requests.get(url, params)
#         soup = BeautifulSoup(response.text, 'lxml')
#         tr_list = soup.select('form#frm_defaultList table > tbody > tr')
#
#         for tr in tr_list:
#             song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
#             if tr.select_one('td:nth-of-type(3) a.fc_gray'):
#                 title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
#             else:
#                 title = '타이틀이 없습니다'
#             artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(strip=True)
#             album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)
#
#             url_song = 'https://www.melon.com/song/detail.htm'
#             params_song = {
#                 'songId': song_id,
#             }
#             response_song = requests.get(url_song, params_song)
#             soup_song = BeautifulSoup(response_song.text, 'lxml')
#
#             thumb_entry = soup_song.find('div', class_='thumb')
#             url_img_cover = thumb_entry.find('img').get('src')
#             if re.findall('http.*?\.jpg', url_img_cover):
#                 url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
#             else:
#                 url_img_cover = "http://cdnimg.melon.co.kr/resource/image/web/default/noAlbum_500_160727.jpg"
#
#             div_entry = soup_song.find('div', class_='entry')
#
#             title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()
#
#             artist = div_entry.find('div', class_='artist').get_text(strip=True)
#             if div_entry.select_one('div.artist a'):
#                 artist_id_a = div_entry.select_one('div.artist a').get('href')
#                 artist_id = re.findall(r'\(\'(.*?)\'\)', artist_id_a)[0]
#             else:
#                 artist_id = "000000"
#             # 앨범, 발매일, 장르...에 대한 Description list
#             dl = div_entry.find('div', class_='meta').find('dl')
#             # isinstance(인스턴스, 클래스(타입))
#             # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
#             items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
#             it = iter(items)
#             description_dict = dict(zip(it, it))
#
#             album = description_dict.get('앨범')
#             album_id_a = str(dl.select_one('a'))
#             if album_id_a:
#                 album_id = re.findall(r'\(\'(.*?)\'\)', album_id_a)[0]
#             else:
#                 album_id = "000000"
#             # release_date = description_dict.get('발매일')
#             genre = description_dict.get('장르')
#
#             div_lyrics = soup_song.find('div', id='d_video_summary')
#
#             lyrics_list = []
#             if div_lyrics:
#                 for item in div_lyrics:
#                     if item.name == 'br':
#                         lyrics_list.append('\n')
#                     elif type(item) is NavigableString:
#                         lyrics_list.append(item.strip())
#                 lyrics = ''.join(lyrics_list)
#             else:
#                 lyrics = '가사가 없습니다'
#
#             song_info_list.append({
#                 'song_id': song_id,
#                 'url_img_cover': url_img_cover,
#                 'artist': artist,
#                 'artist_id': artist_id,
#                 'album': album,
#                 'album_id': album_id,
#                 'title': title,
#                 'genre': genre,
#                 'lyrics': lyrics,
#             })
#         context['song_info_list'] = song_info_list
#     return render(request, 'song/song_search_from_melon.html', context)


def song_search_from_melon(request):
    keyword = request.GET.get('keyword')
    context = {}
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
                title = tr.select_one('td:nth-of-type(3) > div > div > span').get_text(strip=True)

            artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(strip=True)
            album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

            song_info_list.append({
                'song_id': song_id,
                'title': title,
                'artist': artist,
                'album': album,
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

    #     url_song = 'https://www.melon.com/song/detail.htm'
    #     params_song = {
    #         'songId': song_id,
    #     }
    #     response_song = requests.get(url_song, params_song)
    #     soup_song = BeautifulSoup(response_song.text, 'lxml')
    #
    #     thumb_entry = soup_song.find('div', class_='thumb')
    #     url_img_cover = thumb_entry.find('img').get('src')
    #     if re.findall('http.*?\.jpg', url_img_cover):
    #         url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
    #     else:
    #         url_img_cover = "http://cdnimg.melon.co.kr/resource/image/web/default/noAlbum_500_160727.jpg"
    #
    #     div_entry = soup_song.find('div', class_='entry')
    #
    #     title = div_entry.find('div', class_='song_name').strong.next_sibling.strip()
    #
    #     artist = div_entry.find('div', class_='artist').get_text(strip=True)
    #     artist_id_a = div_entry.select_one('div.artist a').get('href')
    #     artist_id = re.findall(r'\(\'(.*?)\'\)', artist_id_a)[0]
    #     # 앨범, 발매일, 장르...에 대한 Description list
    #     dl = div_entry.find('div', class_='meta').find('dl')
    #     # isinstance(인스턴스, 클래스(타입))
    #     # items = ['앨범', '앨범명', '발매일', '발매일값', '장르', '장르값']
    #     items = [item.get_text(strip=True) for item in dl.contents if not isinstance(item, str)]
    #     it = iter(items)
    #     description_dict = dict(zip(it, it))
    #
    #     album = description_dict.get('앨범')
    #     album_id_a = str(dl.select_one('a'))
    #     album_id = re.findall(r'\(\'(.*?)\'\)', album_id_a)[0]
    #     # release_date = description_dict.get('발매일')
    #     genre = description_dict.get('장르')
    #
    #     div_lyrics = soup_song.find('div', id='d_video_summary')
    #
    #     lyrics_list = []
    #     if div_lyrics:
    #         for item in div_lyrics:
    #             if item.name == 'br':
    #                 lyrics_list.append('\n')
    #             elif type(item) is NavigableString:
    #                 lyrics_list.append(item.strip())
    #         lyrics = ''.join(lyrics_list)
    #     else:
    #         lyrics = '가사가 없습니다'
    #
    # # if Album.objects.get(title=album):
    #     response = requests.get(url_img_cover)
    #     binary_data = response.content
    #     temp_file = BytesIO()
    #     temp_file.write(binary_data)
    #     temp_file.seek(0)
    #
    #     song, _ = Song.objects.update_or_create(
    #         song_id=song_id,
    #         defaults={
    #             # 'album': Album.objects.get(title=album),
    #             'title': title,
    #             'genre': genre,
    #             'lyrics': lyrics,
    #         }
    #     )
    #
    #     # artist = ArtistData(artist_id)
    #     # artist.get_detail()
    #     #
    #     # name = artist.name
    #     # url_img_cover = artist.url_img_cover
    #     # url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
    #     # real_name = artist.personal_information.get('본명', '')
    #     # nationality = artist.personal_information.get('국적', '')
    #     # birth_date_str = artist.personal_information.get('생일', '')
    #     # if not birth_date_str or len(birth_date_str) <= 9:
    #     #     birth_date_str = '1900.01.01'
    #     # constellation = artist.personal_information.get('별자리', '')
    #     # blood_type = artist.personal_information.get('혈액형', '')
    #     #
    #     # for short, full in Artist.CHOICES_BLOOD_TYPE:
    #     #     if blood_type.strip() == full:
    #     #         blood_type = short
    #     #         break
    #     #     else:
    #     #         blood_type = Artist.BLOOD_TYPE_OTHER
    #     #
    #     # response = requests.get(url_img_cover)
    #     # binary_data = response.content
    #     # temp_file = BytesIO()
    #     # temp_file.write(binary_data)
    #     # temp_file.seek(0)
    #     #
    #     # artist, _ = Artist.objects.update_or_create(
    #     #     melon_id=artist_id,
    #     #     defaults={
    #     #         'name': name,
    #     #         'real_name': real_name,
    #     #         'nationality': nationality,
    #     #         'birth_date': datetime.strptime(birth_date_str, '%Y.%m.%d'),
    #     #         'constellation': constellation,
    #     #         'blood_type': blood_type,
    #     #     }
    #     # )
    #     #
    #     # file_name = Path(url_img_cover).name
    #     # artist.img_profile.save(file_name, File(temp_file))
    #
    #     artist, _ = Artist.objects.update_or_create_from_melon(artist_id)
    #     song.artists.add(artist)
    #
    #     file_name = Path(url_img_cover).name
    #     song.img_cover.save(file_name, File(temp_file))

        Song.objects.update_or_create_from_song_id(song_id)
    return redirect('song:song-list')