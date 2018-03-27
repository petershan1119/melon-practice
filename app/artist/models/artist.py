from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.fields.files import FieldFile
from django.forms.models import model_to_dict
from django.http import JsonResponse

from .artist_youtube import ArtistYouTube
from youtube.models import Youtube
from .manager import ArtistManager
from django.db.models.fields.files import FieldFile




__all__ = (
    "Artist",
)


class Artist(models.Model):
    BLOOD_TYPE_A = 'a'
    BLOOD_TYPE_B = 'b'
    BLOOD_TYPE_O = 'o'
    BLOOD_TYPE_AB = 'c'
    BLOOD_TYPE_OTHER = 'x'
    CHOICES_BLOOD_TYPE = (
        (BLOOD_TYPE_A, 'A형'),
        (BLOOD_TYPE_B, 'B형'),
        (BLOOD_TYPE_O, 'O형'),
        (BLOOD_TYPE_AB, 'AB형'),
        (BLOOD_TYPE_OTHER, '기타'),
    )

    melon_id = models.CharField(
        '멜론 Artist ID',
        max_length=20,
        blank=True,
        null=True,
        unique=True,
    )

    img_profile = models.ImageField(
        '프로필 이미지',
        upload_to='artist',
        blank=True,
    )
    name = models.CharField(
        '이름',
        max_length=50,
    )
    real_name = models.CharField(
        '본명',
        max_length=30,
        blank=True,
    )
    nationality = models.CharField(
        '국적',
        max_length=50,
        blank=True,
    )
    birth_date = models.DateField(
        '생년월일',
        blank=True,
        null=True,
    )
    constellation = models.CharField(
        '별자리',
        max_length=30,
        blank=True,
    )
    blood_type = models.CharField(
        '혈액형',
        max_length=1,
        choices=CHOICES_BLOOD_TYPE,
        blank=True,
    )
    intro = models.TextField(
        '소개',
        blank=True,
    )
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ArtistLike',
        related_name='like_artists',
        blank=True,
    )
    youtube_links = models.ManyToManyField(
        Youtube,
        blank=True,
    )
    youtube_videos = models.ManyToManyField(
        ArtistYouTube,
        related_name='artists',
        blank=True,
    )

    objects = ArtistManager()

    class Meta:
        pass

    def __str__(self):
        return self.name

    def toggle_like_user(self, user):
        """
        이 User의 특정 Artist를 연결하는 중개모델인s ArtistList인스턴스를
            없을 경우 생성, 있으면 삭제하는 메서드
        """
        # query = ArtistLike.objects.filter(artist=self, user=user)
        # if query.exists():
        #     query.delete()
        #     return False
        # else:
        #     ArtistLike.objects.create(artist=self, user=user)
        #     return True

        like, like_created = self.like_user_info_list.get_or_create(user=user)
        if not like_created:
            like.delete()
        return like_created

    def to_json(self):
        user_class = get_user_model()

        ret = model_to_dict(self)

        # model_to_dict의 결과가 dict
        # 해당 dict의 item을 순회하며
        #   JSON Serialize할때 에러나는 타입의 value를
        #   적절히 변환해서 value에 다시 대입
        def convert_value(value):
            if isinstance(value, FieldFile):
                return value.url if value else None
            elif isinstance(value, user_class):
                return value.pk if value else None
            elif isinstance(value, ArtistYouTube):
                return value.pk if value else None
            elif isinstance(value, Youtube):
                return value.title if value else None
            return value

        def convert_obj(obj):
            """
            객체 또는 컨테이너 객체에 포함된 객체들 중
            직렬화가 불가능한 객체를 가능하도록 형태를 변환해주는 함수
            :param obj:
            :return: convert_value()를 거친 객체
            """
            if isinstance(obj, list):
                # list타입일 경우 각 항목을 순회하며 index에 해당하는 값을 변환
                for index, item in enumerate(obj):
                    obj[index] = convert_obj(item)
            elif isinstance(obj, dict):
                # dict타입일 경우 각 항목을 순회하며 key에 해당하는 값을 변환
                for key, value in obj.items():
                    obj[key] = convert_obj(value)
            # list나 dict가 아닐 경우, 객체 자체를 변환한 값을 리턴
            return convert_value(obj)

        convert_obj(ret)
        return ret