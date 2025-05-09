"""
支付相关URL配置
"""
from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    # 支付
    path('', views.PaymentView.as_view(), name='payment'),
    
    # 支付回调
    path('notify/', views.PaymentNotifyView.as_view(), name='notify'),
]