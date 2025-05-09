"""
内容相关URL配置
"""
from django.urls import path
from . import views

app_name = 'contents'

urlpatterns = [
    # 广告内容
    path('contents/', views.ContentView.as_view(), name='content'),
    path('contents/<int:content_id>/', views.ContentView.as_view(), name='content_detail'),
    
    # 广告分类
    path('categories/', views.ContentCategoryView.as_view(), name='category'),
    
    # 首页内容
    path('index/', views.IndexContentView.as_view(), name='index'),
] 