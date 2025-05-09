"""
用户相关URL配置
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # 用户注册
    path('register/', views.UserRegisterView.as_view(), name='register'),
    
    # 用户登录
    path('login/', views.UserLoginView.as_view(), name='login'),
    
    # 用户登出
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    
    # 用户资料
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # 用户地址
    path('addresses/', views.UserAddressView.as_view(), name='addresses'),
]