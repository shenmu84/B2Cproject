from django.urls import path
from goods .views import index
urlpatterns = [
    path('index/',index)
]