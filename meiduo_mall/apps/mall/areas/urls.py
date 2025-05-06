from django.urls import path
from apps.mall.areas.views import *
urlpatterns=[
    path('areas/',AreasView.as_view()),
path('areas/<id>/',SubAreasView.as_view())
]