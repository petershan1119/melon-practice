from datetime import datetime
from django.core.files import File
from django.db import models

from crawler.artist import ArtistData
from utils.file import download


__all__ = (
    "ArtistManager",
)


class ArtistManager(models.Manager):

    def update_or_create_from_melon(self, artist_id):
        from .artist import Artist
        artist = ArtistData(artist_id)
        artist.get_detail()

        name = artist.name
        url_img_cover = artist.url_img_cover
        # url_img_cover = re.findall('http.*?\.jpg', url_img_cover)[0]
        real_name = artist.personal_information.get('본명', '')
        nationality = artist.personal_information.get('국적', '')
        birth_date_str = artist.personal_information.get('생일', '')

        try:
            birth_date = datetime.strptime(birth_date_str, '%Y.%m.%d')
        except ValueError:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y.%m')
            except ValueError:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y')
                except ValueError:
                    birth_date = None

        constellation = artist.personal_information.get('별자리', '')


        blood_type = artist.personal_information.get('혈액형', '')
        # blood_type과 birth_date_str이 없을때 처리할것

        # 튜플의 리스트를 순회하며 blood_type을 결정
        for short, full in Artist.CHOICES_BLOOD_TYPE:
            if blood_type.strip() == full:
                blood_type = short
                break
        else:
            # break가 발생하지 않은 경우
            # (미리 정의해놓은 혈액형 타입에 없을 경우)
            # 기타 혈액형값으로 설정
            blood_type = Artist.BLOOD_TYPE_OTHER

        # response = requests.get(url_img_cover)
        # binary_data = response.content
        # temp_file = BytesIO()
        # temp_file.write(binary_data)
        # # temp_file.seek(0)

        if request.method == 'POST':
            artist_id = request.POST['artist_id']
            Artist.objects.update_or_create_from_melon(artist_id)
            return redirect('artist:artist-list')

        # file_name = Path(url_img_cover).name
        # temp_file.seek(0)
        # mine_type = magic.from_buffer(temp_file.read(), mime=True)
        # file_name = '{artist_id}.{ext}'.format(
        #     artist_id=artist_id,
        #     ext=mine_type.split('/')[-1]
        # )
        file_name, temp_file = download(url_img_cover, artist_id)

        if artist.img_profile:
            artist.img_profile.delete()
        artist.img_profile.save(file_name, File(temp_file))

        # if not artist.img_profile:
        #     artist.img_profile.save(file_name, File(temp_file))
        return artist, artist_created