from django.urls import path
from apps.mall.carts.views import *
urlpatterns = [
    path('carts/', CartsView.as_view()),
    ]