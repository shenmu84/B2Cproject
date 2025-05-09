"""
商品相关URL配置
"""
from django.urls import path
from . import views

app_name = 'goods'

urlpatterns = [
    # 商品分类
    path('categories/', views.CategoryView.as_view(), name='categories'),
    
    # 商品频道
    path('channels/', views.ChannelView.as_view(), name='channels'),
    
    # SKU列表
    path('skus/', views.SKUListView.as_view(), name='sku_list'),
    
    # SKU详情
    path('skus/<int:sku_id>/', views.SKUDetailView.as_view(), name='sku_detail'),
    
    # SKU规格
    path('skus/<int:sku_id>/specs/', views.SKUSpecificationView.as_view(), name='sku_specs'),
    
    # 热门商品
    path('hot/', views.SKUHotView.as_view(), name='hot'),
]