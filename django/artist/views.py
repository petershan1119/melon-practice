import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from django.conf import settings
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from youtube.models import Youtube
from .forms import ArtistForm
from crawler.artist import ArtistData
from .models import Artist, ArtistLike


def artist_list(request):
    artists = Artist.objects.all()
    context = {
        'artists': artists,
    }
    return render(request, 'artist/artist_list.html', context)


def artist_add(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('artist:artist-list')
    else:
        form = ArtistForm()

    context = {
        'artist_form': form,
    }
    return render(request, 'artist/artist_add.html', context)


def artist_like_toggle(request, artist_pk):
    """
    request.user와
    artist_pk를 사용해서

    ArtistLike객체를 토글하는 뷰

    완료 후에는 artist:artist-list로 이동
    """
    artist = Artist.objects.get(pk=artist_pk)
    if request.method == "POST":
        artist.toggle_like_user(user=request.user)
        next_path = request.POST.get('next-path', 'artist:artist-list')
        return redirect(next_path)


def artist_edit(request, artist_pk):
    """
    artist_pk에 해당하는 Artist 수정

    Form: ArtistForm
    Template: artist/artsit_edit.html

    bound form: ArtistForm(instance=<artist instance>)
    ModelForm을 사용해 instance 업데이트
        ArtistForm(request.POST, instance=<artist instance>)
        form.save()
    """
    artist = get_object_or_404(Artist, pk=artist_pk)
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            return redirect('artist:artist-list')
    else:
        form = ArtistForm(instance=artist)
    context = {
        'artist_form': form,
    }
    return render(request, 'artist/artist_edit.html', context)


def artist_search_from_melon(request):
    context = {}
    if request.method == "POST":
        keyword = request.POST['keyword']
        if keyword:
            artist_info_list = []
            url = 'https://www.melon.com/search/artist/index.htm'
            params = {
                'q': keyword,
            }
            response = requests.get(url, params)
            soup = BeautifulSoup(response.text, 'lxml')
            for li in soup.select('div.list_atist12.d_artist_list > ul > li'):
                dl = li.select_one('div.atist_info > dl')
                href = li.select_one('a.thumb').get('href')
                p = re.compile(r"goArtistDetail\('(\d+)'\)")

                name = dl.select_one('dt:nth-of-type(1) > a').get_text(strip=True)
                url_img_cover = li.select_one('a.thumb img').get('src')
                artist_id = re.search(p, href).group(1)

                artist_info_list.append({
                    'name': name,
                    'url_img_cover': url_img_cover,
                    'artist_id': artist_id,
                    'is_exist': Artist.objects.filter(melon_id=artist_id).exists(),
                })
            context['artist_info_list'] = artist_info_list
    return render(request, 'artist/artist_search_from_melon.html', context)


def artist_add_from_melon(request):
    """
    1. artist_search_from_melon.html에
        form을 작성 (action이 현재 이 view로 올 수 있도록), POST메서드
            필요한 요소는 csrf_token과
                type=hidden으로 전달하는 artist_id값
                <input type="hidden" value="{{ artist_info.artist_id }}">
                button submit (추가하기)
    2. 작성한 form
    POST요청을 받음 (추가하기 버튼 클릭)
    request.POST['artist_id']
    :param request:
    :return:
    """
    if request.method == 'POST':
        artist_id = request.POST['artist_id']
        Artist.objects.update_or_create_from_melon(artist_id)
        return redirect('artist:artist-list')


def artist_detail(request, artist_pk):
    artist = get_object_or_404(Artist, pk=artist_pk)

    url = 'https://www.googleapis.com/youtube/v3/search'
    # params = {
    #     'key': settings.YOUTUBE_API_KEY,
    #     'part': 'snippet',
    #     'q': artist.name,
    #     'maxResults': 20,
    # }
    params = {
        'key': settings.YOUTUBE_API_KEY,
        'part': 'snippet',
        'type': 'video',
        'maxResults': '10',
        'q': artist.name,
    }


    response = requests.get(url, params)
    response_dict = response.json()

    # videos = []
    # channels = []
    # playlists = []
    #
    # for search_result in response_dict['items']:
    #     if search_result['id']['kind'] == 'youtube#video':
    #         videos.append({
    #             'title': search_result["snippet"]["title"],
    #             'video_id': search_result["id"]["videoId"],
    #         })
    #     elif search_result['id']['kind'] == 'youtube#channel':
    #         channels.append({
    #             'title': search_result["snippet"]["title"],
    #             'channel_id': search_result["id"]["channelId"],
    #         })
    #     elif search_result["id"]["kind"] == "youtube#playlist":
    #         playlists.append({
    #             'title': search_result["snippet"]["title"],
    #             'playlist_id': search_result["id"]["playlistId"],
    #         })
    #
    # for video in videos[:10]:
    #     if not Youtube.objects.filter(video_id=video['video_id']):
    #         y_object = Youtube.objects.create(video_id=video['video_id'], title=video['title'])
    #         artist.youtube_links.add(y_object)
    #
    # youtube_list = []
    # url_youtube = 'https://www.youtube.com/watch?v='
    #
    # for item in artist.youtube_links.all():
    #     title = item.title
    #     video_id = item.video_id
    #     youtube_list.append({
    #         'title': title,
    #         'video_id': url_youtube + video_id,
    #     })
    #
    # context = {
    #     'artist': artist,
    #     'youtube_list': youtube_list,
    # }

    context = {
        'artist': artist,
        'youtube_items': response_dict['items'],
    }
    return render(request, 'artist/artist_detail.html', context)