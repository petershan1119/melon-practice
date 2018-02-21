import re
import requests
from bs4 import BeautifulSoup
from django.shortcuts import render, redirect

from .models import Artist

def artist_list(request):
    artists = Artist.objects.all()
    context = {
        'artists': artists,
    }
    return render(request, 'artist/artist_list.html', context)


def artist_add(request):
    if request.method == 'POST':
        name = request.POST['name']
        Artist.objects.create(
            name=name,
        )
        return redirect('artist:artist-list')
    else:
        return render(request, 'artist/artist_add.html')


def artist_search_from_melon(request):
    context = {}
    if request.method == "POST":
        keyword = request.POST['keyword']
        if keyword:
            artist_info_list = []=
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
                })
            context['artist_info_list'] = artist_info_list
    return render(request, 'artist/artist_search_from_melon.html', context)