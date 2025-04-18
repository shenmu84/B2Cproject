from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_page, name='login'),
    path('login/<str:provider>/', views.social_login, name='social_login'),
    path('callback/', views.callback, name='callback'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
]