from django.urls import path
from apps.users.views import *
urlpatterns=[
    path('carts/simple/',tentative.as_view()),
    path('register/',post_json),
    path('info/',CenterView.as_view()),
    path('emails/',EmailView.as_view()),
    path('emails/verification/',EmailVerifyView.as_view()),

    path('logout/',LogoutView.as_view()),
    path('mobiles/<mobile>/count/',MobileCountView.as_view()),
    path('log',log),
    path('login/',LoginView.as_view()),
    path('usernames/<username:username>/count/',UsernameCountView.as_view()),
    path('log/',log),
    path('addresses/create/',AddressCreateView.as_view()),
    path('addresses/',AddressView.as_view()),

    path('browse_histories/', UserHistoryView.as_view()),
]