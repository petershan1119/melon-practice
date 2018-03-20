from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from artist.permissions import IsOwnerOrReadOnly
from artist.serializers import ArtistSerializer
from utils.pagination import SmallPagination
from ...models import Artist


__all__ = (
    'ArtistListCreateView',
    'ArtistRetrieveUpdateDestroyView',
)


class ArtistListView(APIView):
    # generics의 요소를 사용해서
    # ArtistListCreateView,
    # ArtistRetrieveUpdateDestroyView
    #   2개를 구현
    #   URL과 연결
    #   Postman에 API테스트 구현
    #   다 실행해보기
    #   Pagination으로 5개씩만 오도록
    def get(self, request):
        artists = Artist.objects.all()
        serializer = ArtistSerializer(artists, many=True)
        return Response(serializer.data)


class ArtistListCreateView(generics.ListCreateAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    pagination_class = SmallPagination

    def get(self, request, *args, **kwargs):
        print('request.users', request.user)
        return super().get(request, *args, **kwargs)

    # permission_classes = (
    #     permissions.IsAuthenticatedOrReadOnly,
    #     IsOwnerOrReadOnly,
    # )
    # def perform_create(self, serializer):
    #     serializer.save(owner=self.request.user)


class ArtistRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    )