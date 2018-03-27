from django.urls import path

from .. import apis

urlpatterns = [
    path('auth-token/', apis.AuthTokenView.as_view()),
    path('info/', apis.MyUserDetail.as_view()),
    path('facebook-auth-token/', apis.AuthTokenForFacebookAccessTokenView.as_view()),
]