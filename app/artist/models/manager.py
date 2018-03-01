from datetime import datetime

from django.core.files import File
from django.db import models

from crawler.artist import ArtistData
from utils.file import download, get_buffer_ext

__all__ = (
    'ArtistManager',
)


class ArtistManager(models.Manager):
    def update_or_create_from_melon(self, artist_id):
        from .artist import Artist
        artist = ArtistData(artist_id)
        artist.get_detail()
        name = artist.name
        url_img_cover = artist.url_img_cover
        real_name = artist.personal_information.get('본명', '')
        nationality = artist.personal_information.get('국적', '')
        birth_date_str = artist.personal_information.get('생일', '')
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

        artist, artist_created = self.update_or_create(
            melon_id=artist_id,
            defaults={
                'name': name,
                'real_name': real_name,
                'nationality': nationality,
                'birth_date': datetime.strptime(
                    birth_date_str, '%Y.%m.%d') if birth_date_str else None,
                'constellation': constellation,
                'blood_type': blood_type,
            }
        )
        # img_profile필드에 저장할 파일확장자를 바이너리 데이터 자체의 MIME_TYPE에서 가져옴
        # 파일명은 artist_id를 사용
        temp_file = download(url_img_cover)
        file_name = '{artist_id}.{ext}'.format(
            artist_id=artist_id,
            ext=get_buffer_ext(temp_file),
        )
        # artist.img_profile필드의 save를 따로 호출, 이름과 File객체를 전달
        #   (Django)File객체의 생성에는 (Python)File객체를 사용,
        #           이 때 (Python)File객체처럼 취급되는 BytesIO를 사용
        if artist.img_profile:
            artist.img_profile.delete()
        artist.img_profile.save(file_name, File(temp_file))
        return artist, artist_created