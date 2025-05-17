from django.urls import path
from apps.areas.views import *
urlpatterns=[
    path('areas/',AreasView.as_view()),
path('areas/<id>/',SubAreasView.as_view())
]