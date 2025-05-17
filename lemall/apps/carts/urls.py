from django.urls import path
from apps.carts.views import *

from utils import views

urlpatterns = [
    path('carts/', CartsView.as_view()),
    ]