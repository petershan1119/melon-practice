import re
from io import BytesIO
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from datetime import datetime

from django.core.files import File
from django.shortcuts import render, redirect

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
                })
            context['artist_info_list'] = artist_info_list
    return render(request, 'artist/artist_search_from_melon.html', context)

def artist_add_from_melon(request):
    if request.method == 'POST':
        artist_id = request.POST['artist_id']
        artist = ArtistData(artist_id)
        artist.get_detail()

        name = artist.name
        url_img_cover = artist.url_img_cover
        url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
        real_name = artist.personal_information.get('본명', '')
        nationality = artist.personal_information.get('국적', '')
        birth_date_str = artist.personal_information.get('생일', '')
        if not birth_date_str or len(birth_date_str) <= 8:
            birth_date_str = '1900.01.01'
        constellation = artist.personal_information.get('별자리', '')
        blood_type = artist.personal_information.get('혈액형', '')

        for short, full in Artist.CHOICES_BLOOD_TYPE:
            if blood_type.strip() == full:
                blood_type = short
                break
        else:
            blood_type = Artist.BLOOD_TYPE_OTHER

        response = requests.get(url_img_cover)
        binary_data = response.content
        temp_file = BytesIO()
        temp_file.write(binary_data)
        temp_file.seek(0)

        artist, _ = Artist.objects.update_or_create(
            melon_id=artist_id,
            defaults={
                'name': name,
                'real_name': real_name,
                'nationality': nationality,
                'birth_date': datetime.strptime(birth_date_str, '%Y.%m.%d'),
                'constellation': constellation,
                'blood_type': blood_type,
            }
        )

        file_name = Path(url_img_cover).name
        artist.img_profile.save(file_name, File(temp_file))
        return redirect('artist:artist-list')