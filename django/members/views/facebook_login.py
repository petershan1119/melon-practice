import requests
from django.conf import settings
from django.contrib.auth import get_user_model, login, authenticate
from django.http import HttpResponse
from django.shortcuts import redirect

__all__ = (
    'facebook_login',
)

User = get_user_model()

def facebook_login(request):
    code = request.GET.get('code')
    user = authenticate(request, code=code)
    login(request, user)
    return redirect('index')


def facebook_login_backup(request):
    client_id = settings.FACEBOOK_APP_ID
    client_secret = settings.FACEBOOK_SECRET_CODE
    code = request.GET['code']
    redirect_uri = 'http://localhost:8000/facebook-login/'
    url = 'https://graph.facebook.com/v2.12/oauth/access_token'

    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'client_secret': client_secret,
        'code': code,
    }
    response = requests.get(url, params)
    response_dict = response.json()
    for key, value in response_dict.items():
        print(f'{key}: {value}')

    # GraphAPI의 me 엔드포인트에 GET 요청 보내기
    url = 'https://graph.facebook.com/v2.12/me'
    params = {
        'access_token': response_dict['access_token'],
        'fields': ','.join([
            'id',
            'name',
            'picture.width(2500)',
            'first_name',
            'last_name',
        ])
    }

    # "{
    #   'id': '1639895212763666',
    #   'name': 'Sang Won Han',
    #   'picture': {
    #       'data': {
    #           'height': 640,
    #           'is_silhouette': False,
    #           'url': 'https://scontent.xx.fbcdn.net/v/t1.0-1/387122_185074364912432_1806965393_n.jpg?oh=9b04429ffe4cba685ee13d8551bc6a13&oe=5AFFA211',
    #       '   width': 480
    #       }
    #   },
    #   'first_name': 'Sang Won',
    #   'last_name': 'Han'
    # }

    response = requests.get(url, params)
    response_dict = response.json()
    facebook_id = response_dict['id']
    name = response_dict['name']
    first_name = response_dict['first_name']
    last_name = response_dict['last_name']
    url_picture = response_dict['picture']['data']['url']

    if User.objects.filter(username=facebook_id):
        user = User.objects.get(username=facebook_id)
    else:
        user = User.objects.create(
            username=facebook_id,
            first_name=first_name,
            last_name=last_name,
        )
    login(request, user)
    return redirect('index')
