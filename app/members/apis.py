from rest_framework.authtoken.models import Token
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.response import Response
from rest_framework.views import APIView


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
        return Response({'token': token.key})