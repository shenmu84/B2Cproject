"""
订单相关URL配置
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # 订单
    path('', views.OrderView.as_view(), name='order'),
    
    # 订单详情
    path('<str:order_id>/', views.OrderDetailView.as_view(), name='order_detail'),
]