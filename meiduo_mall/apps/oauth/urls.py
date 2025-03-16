from apps.oauth.views import *
from django.urls import path
urlpatterns = [
    path('qq/authorization/',QQLoginURLView.as_view()),
    path('oauth_callback/',OauthQQView.as_view())
]