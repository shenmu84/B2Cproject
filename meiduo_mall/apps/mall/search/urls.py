"""
搜索相关URL配置
"""
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    # 搜索
    path('', views.SearchView.as_view(), name='search'),
    
    # 搜索建议
    path('suggest/', views.SearchSuggestView.as_view(), name='suggest'),
    
    # 热门搜索
    path('hot/', views.SearchHotView.as_view(), name='hot'),
] 