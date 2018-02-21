from typing import NamedTuple

import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from django.shortcuts import render

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
            # song_id = tr.select_one('td:nth-of-type(1) input[type=checkbox]').get('value')
            title = tr.select_one('td:nth-of-type(3) a.fc_gray').get_text(strip=True)
            # artist = tr.select_one('td:nth-of-type(4) span.checkEllipsisSongdefaultList').get_text(strip=True)
            album = tr.select_one('td:nth-of-type(5) a').get_text(strip=True)

            song_info_list.append({
                # 'song_id': song_id,
                'title': title,
                # 'artist': artist,
                'album': album,
            })
        context['song_info_list'] = song_info_list
    return render(request, 'song/song_search_from_melon.html', context)

def song_add_from_melon(request):
    # 패키지 분할 (artist랑 똑같은 형태로)
    # artist_add_from_melon과 같은 기능을 함
    #   song_search_from_melon도 구현
    #       -> 이 안에 'DB에 추가'하는 Form구현
    pass