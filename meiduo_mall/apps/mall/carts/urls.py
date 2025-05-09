"""
购物车相关URL配置
"""
from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    # 购物车
    path('', views.CartView.as_view(), name='cart'),
    
    # 购物车选择
    path('select/', views.CartSelectView.as_view(), name='select'),
]