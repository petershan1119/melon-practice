import re
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect, get_object_or_404

from .forms import AlbumForm
from .models import Album


def album_list(request):
    albums = Album.objects.all()
    context = {
        'albums': albums,
    }
    return render(request, 'album/album_list.html', context)

def album_add(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('album:album-list')
    else:
        form = AlbumForm()

    context = {
        'album_form': form,
    }
    return render(request, 'album/album_add.html', context)


def album_search_from_melon(request):
    context = {}
    if request.method == "POST":
        keyword = request.POST['keyword']
        if keyword:
            album_info_list = []
            url = 'https://www.melon.com/search/album/index.htm'
            params = {
                'q': keyword,
            }
            response = requests.get(url, params)
            soup = BeautifulSoup(response.text, 'lxml')

            for li in soup.select('div#pageList div.list_album11 ul.album11_ul li.album11_li'):
                img_cover = li.select_one("div.wrap_album04 img").get('src')
                title = li.select_one('div.atist_info a').get_text(strip=True)
                melon_id_href = li.select_one('div.atist_info a').get('href')
                melon_id = re.findall(r"goAlbumDetail\('(.*?)'\);$", melon_id_href)[0]
                release_date = li.select_one('div.atist_info dd.wrap_btn span.cnt_view').get_text(strip=True)

                album_info_list.append({
                    'melon_id': melon_id,
                    'img_cover': img_cover,
                    'title': title,
                    'release_date': release_date,
                    'is_exist': Album.objects.filter(melon_id=melon_id).exists(),
                })
            context['album_info_list'] = album_info_list
    return render(request, 'album/album_search_from_melon.html', context)


def album_add_from_melon(request):
    if request.method == "POST":
        melon_id = request.POST['melon_id']
        Album.objects.update_or_create_from_melon(melon_id)
        return redirect('album:album-list')


def album_detail(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk)
    context = {
        "album": album,
    }
    return render(request, 'album/album_detail.html', context)


def album_edit(request, album_pk):
    album = get_object_or_404(Album, pk=album_pk)
    if request.method == "POST":
        form = AlbumForm(request.POST, request.FILES, instance=album)
        if form.is_valid():
            form.save()
            return redirect('album:album-list')
    else:
        form = AlbumForm(instance=album)
    context = {
        'album_form': form,
    }
    return render(request, 'album/album_edit.html', context)

def album_like_toggle(request, album_pk):
    album = Album.objects.get(pk=album_pk)
    if request.method == "POST":
        album.toggle_like_user(user=request.user)
        next_path = request.POST.get('next-path', 'album:album-list')
        return redirect(next_path)