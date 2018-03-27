# import random
#
# from django.test import TestCase
# from django.urls import reverse, resolve
# from rest_framework import status
#
# from rest_framework.test import APITestCase
#
# from artist.models import Artist
# from artist.serializers import ArtistSerializer
# from .apis import ArtistListCreateView
#
#
# class ArtistListTest(APITestCase):
#     VIEW = ArtistListCreateView
#     PATH = '/apis/artist/'
#     VIEW_NAME = 'apis:artist:artist-list'
#     PAGINATION_COUNT = 5
#
#     def test_reverse(self):
#         f"""
#         Artist List에 해당하는 VIEW_NAME을 reverse한 결과가 기대 PATH와 같은지 검사
#             VIEW_NAME:  {self.VIEW_NAME}
#             PATH:       {self.PATH}
#         :return:
#         """
#         # 기대하는 URL path /apis/artist
#         #
#         # artist-list에 해당하는 URL name을 reverse했을 때,
#         # 우리가 기대하는 URL path와 일치하는 테스트
#         #   -> Django url reverse
#         #
#         self.assertEqual(reverse(self.VIEW_NAME), self.PATH)
#
#     def test_resolve(self):
#         f"""
#         Aritst List에 해당하는 PATH를 resolve한 결과의 func와 view_name이
#         기대하는 View.as_view()와 VIEW_NAME과 같은지 검사
#             PATH:       {self.PATH}
#             VIEW_NAME:  {self.VIEW_NAME}
#         :return:
#         """
#         # 기대하는 View function: ArtistListCreateView.as_view()
#         # 기대하는 URL name: apis:artist:artist-list'
#         # artist-list에 해당하는 URL path를 resolve했을 때,
#         # 1. ResolverMatch obj의 func의 __name__속성이
#         #   우리가 기대하는 View function의 __name__속성과 같은지
#         # 2. ResolverMatch obj의 view_name이 우리가 기대하는
#         path = self.PATH
#         resolver_match = resolve(path)
#         self.assertEqual(
#             resolver_match.func.__name__,
#             self.VIEW.as_view().__name__,
#         )
#         self.assertEqual(
#             resolver_match.view_name,
#             self.VIEW_NAME,
#         )
#
#     def test_artist_list_count(self):
#         num = random.randrange(1,10)
#         for i in range(num):
#             Artist.objects.create(name=f'Artist{i}')
#
#         # self.client에 get요청
#         # response.data를 사용
#         #
#         # artist-list요청시 알 수 있는 전체 Artist계수가 기대값과 같은지 테스트
#         #   (테스트용 Artist를 여러개 생성해야 함)
#         response = self.client.get(self.PATH)
#         self.assertEqual(
#             response.data['count'],
#             self.MODEL.objecs.count(),
#         )
#         self.assertEqual(
#             response.data['count'],
#             num,
#         )
#
#     def test_artist_list_pagination(self):
#         # math.cell <- 소수점 올림
#         num = 13
#         for i in range(num):
#             Artist.objects.create(name=f'Artist{i+1}')
#         response = self.client.get(self.PATH, {'page': 1})
#
#         # 응답코드 200 확인
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         # for문을 사용해서, 아래의 로직이 페이지네이션 된 모든 page들에 요청 후 results값을 확인하도록 구성
#
#         # 'results'키에 5개의 데이터가 배열로 전달되는지 확인
#         self.assertEqual(
#             len(response.data['results']),
#             self.PAGINATION_COUNT,
#         )
#
#         # 'results'키에 들어있는 5개의 Artist가 serialize되어있는 결과가
#         # 실제 QuerySet을 serialize한 결과와 같은지 확인
#         self.assertEqual(
#            response.data['results'],
#             ArtistSerializer(Artist.objects.all()[:5], many=True).data,
#         )
#
#
# class ArtistCreateTest(APITestCase):
#     def test_create_post(self):
#         # /static/test/pby25.jpg에 있는 파일을 사용해서
#         # 나머지 데이터를 채워서 Artist객체를 생성
#         # 파일을 이진데이터로 읽어서 생성하면 됩니다
#         # 생성할 Artist의 '파일 필드 명'으로 전달
#         #
#         pass
import filecmp
import random

import math

import os

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import DefaultStorage, default_storage
from django.core.files.temp import NamedTemporaryFile
from django.urls import reverse, resolve
from django.utils.module_loading import import_string
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from artist.serializers import ArtistSerializer
from .models import Artist
from .apis import ArtistListCreateView

User = get_user_model()


class ArtistListTest(APITestCase):
    MODEL = Artist
    VIEW = ArtistListCreateView
    PATH = '/apis/artist/'
    VIEW_NAME = 'apis:artist:artist-list'
    PAGINATION_COUNT = 5

    def test_reverse(self):
        # 기대하는 URL path: /apis/artist/
        # artist-list에 해당하는 URL name을 reverse했을 때
        # 우리가 기대하는 URL path와 일치하는지 테스트
        # -> Django url reverse
        self.assertEqual(reverse(self.VIEW_NAME), self.PATH)

    def test_resolve(self):
        # 기대하는 view function: ArtistListCreateView.as_view()
        # 기대하는 URL name: 'apis:artist:artist-list'
        #
        # artist-list에 해당하는 URL path를 resolve했을 때
        # 1. ResolveMatch obj의 func가 우리의 __name__속성이
        #   우리가 기대하는 view function의 __name__속성과 같은지
        # 2. ResolveMath obj의 view_name이 우리가 기대하는 URL name과 같은지 테스트
        #   -> django url resolve, django resolver math
        # resove(): URL path으로부터 view function 가져와
        # ResolveMatch object: resolved URL에 대한 메타정보 접근
        resolver_match = resolve(self.PATH)
        self.assertEqual(
            resolver_match.func.__name__,
            self.VIEW.as_view().__name__,
        )
        self.assertEqual(
            resolver_match.view_name,
            self.VIEW_NAME,
        )

    def test_artist_list_count(self):
        num = random.randrange(10, 20)
        for i in range(num):
            Artist.objects.create(name=f'Artist{i}')

        response = self.client.get(self.PATH)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['count'],
            self.MODEL.objects.count(),
        )
        self.assertEqual(
            response.data['count'],
            num,
        )

    def test_artist_list_pagination(self):
        # math.ceil <- 소수점 올림
        num = 13
        for i in range(num):
            Artist.objects.create(name=f'Artist{i + 1}')
        response = self.client.get(self.PATH, {'page': 1})

        # 응답코드 200 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # for문을 사용해서, 아래의 로직이
        #   페이지네이션 된 모든 page들에 요청 후 results값을 확인하도록 구성

        # 'results'키에 5개의 데이터가 배열로 전달되는지 확인
        self.assertEqual(
            len(response.data['results']),
            self.PAGINATION_COUNT,
        )
        # # 'results'키에 들어있는 5개의 Artist가 serialize되어있는 결과가
        # # 실제 QuerySet을 serialize한 결과와 같은지 확인
        self.assertEqual(
            response.data['results'],
            ArtistSerializer(Artist.objects.all()[:5], many=True).data,
        )

class ArtistCreateTest(APITestCase):
    PATH = '/apis/artist/'
    TEST_ARTIST_NAME = '아이유'

    @staticmethod
    def create_user(username='abcd'):
        return User.objects.create_user(username=username)

    def test_create_post(self):
        # /static/test/suji.jpg에 있는 파일을 이용해서
        # 나머지 데이터를 채워서 Artist객체를 생성
        # 이진데이터 모드로 연 '파일 객체'를
        # 생성할 Artist의 '파일 필드 명'으로 전달
        # self.client.post(URL, {'img_profile': <파일객체>}
        user = self.create_user()
        # self.client.force_authenticate(user=user)
        # User.objects.create_user('example', '', 'abcd1234')
        # self.client.login(username='example', password='abcd1234')


        # token = Token.objects.create(user=user)
        # self.client.credentials(
        #     HTTP_AUTHORIZATION=' Token ' + token.key,
        # )

        self.client.force_authenticate(user=user)
        file_path = os.path.join(settings.STATIC_DIR, 'test', 'suji.jpg')
        with open(file_path, 'rb') as img_profile:
            response = self.client.post(self.PATH, {'img_profile': img_profile, 'name': '아이유'})


        # self.assertEqual(
        #     response.data,
        #     ArtistSerializer(Artist.objects.first()).data,
        # )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(
            Artist.objects.first().name,
            self.TEST_ARTIST_NAME,
        )
        self.assertEqual(
            Artist.objects.count(),
            1,
        )
        # Artist인스턴스에 지정되어있는 파일과
        # -> DEFAULT_FILE_STORAGE를 사용해 저장된 파일
        # Static폴더에 있던 파일
        # -> STATICFILES_STORAGE로 불러온 파일
        artist = Artist.objects.first()

        # FieldFile
        uploaded_file = default_storage.open(
            artist.img_profile.name,
        )
        # uploaded_file_path = uploaded_file.name

        # static_storage_class = import_string(settings.STATICFILES_STORAGE)
        # static_storage = static_storage_class()
        # static_file = static_storage.open(
        #     'test/suji.jpg',
        # )
        # static_file_path = static_file.name
        #
        # filecmp.cmp(uploaded_file_path, static_file_path)

        # 파일을 읽어서 파일시스템상의 임시파일을 생성
        # with NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
        with NamedTemporaryFile() as temp_file:
            temp_file.write(uploaded_file.read())
            self.assertTrue(filecmp.cmp(file_path, temp_file.name))