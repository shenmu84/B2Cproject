
from django.urls import path

from apps.RecomSys.views import *

urlpatterns=[
    path('recommend/',recommend)
]