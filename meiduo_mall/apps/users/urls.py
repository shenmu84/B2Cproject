from django.urls import path
from apps.users.views import *
urlpatterns=[
    path('register/',post_json),
    path('mobiles/<mobile>/count/',MobileCountView.as_view()),
    path('log',log),
path('login/',LoginView.as_view()),
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('log/',log),
]