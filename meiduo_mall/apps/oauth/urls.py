from apps.oauth.views import *
from django.urls import path
urlpatterns = [
    path('qq/authorization/',GITEELoginURLView.as_view()),
    path('oauth_callback/',OauthGITEEView.as_view())
]