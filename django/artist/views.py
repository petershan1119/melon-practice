import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ArtistForm
from crawler.artist import ArtistData
from .models import Artist


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