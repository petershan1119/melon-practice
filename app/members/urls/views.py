from django.urls import path, include

from .. import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('facebook-login/', views.facebook_login, name='facebook-login'),
    # path('sms/', include('sms.urls')),
]