from django.urls import path
from apps.mall.goods.views import *

urlpatterns = [
    path('index/', IndexView.as_view()),
    path('list/<category_id>/skus/',ListView.as_view()),
    path('hot/<category_id>/', HotView.as_view()),
    path('search/',SKUSearchView()),
    path('detail/<sku_id>/', DetailView.as_view()),
    path('detail/visit/<category_id>/',CategoryVisitCountView.as_view()),

]