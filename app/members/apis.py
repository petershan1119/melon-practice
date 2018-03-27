import requests
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView

from members.serializers import UserSerializer, AccessTokenSerializer

User = get_user_model()


class AuthTokenForFacebookAccessTokenView(APIView):
    def post(self, request):
        serializer = AccessTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)

        # def get_user_info(user_access_token):
        #     params = {
        #         'access_token': user_access_token,
        #         'fields': ','.join([
        #             'id',
        #             'name',
        #             'picture.width(2500)',
        #             'first_name',
        #             'last_name',
        #         ])
        #     }
        #     response = requests.get('https://graph.facebook.com/v2.12/me', params)
        #     response_dict = response.json()
        #     return response_dict
        #
        # access_token = request.data['access_token']
        # user_info = get_user_info(access_token)
        #
        # return Response(user_info)

class AuthTokenView(APIView):
    serializer_class = AuthTokenSerializer

    def post(self, request):
        # URL: api/members/auth-token/
        # username, password를 받음
        # 유저 인증에 성공했을 경우
        # 토큰을 생성하거나 있으면 존재하는 걸 가져와서
        # Response로 돌려줌

        # username = request.data.get('username')
        # password = request.data.get('password')
        # user = authenticate(username=username, password=password)
        # if user is not None:
        #     token, _ = Token.objects.get_or_create(user=user)
        #     data = {
        #         'token': token.key
        #     }
        #     return Response(data)
        # raise APIException('authenticate failure')
        # raise AuthenticationFailed()

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        data = {
            'token': token.key,
            'user': UserSerializer(user).data,
        }
        return Response(data)


# class UserDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer


class MyUserDetail(APIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }

    def get(self, request):
        if request.user:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)