
from django.urls import path

from apps.RecomSys.views import *

urlpatterns=[
    path('test/',PersonalizedRecom)

]