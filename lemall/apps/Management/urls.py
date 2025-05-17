# urls.py
from django.shortcuts import render
from django.urls import path
from apps.Management import views

urlpatterns = [
    #1.时间序列化（每天汇总）
    path('get_behavior_daily_data/', views.get_behavior_daily_data),

    #时间序列化（最新一天按小时）
    path('get_behavior_latest_day_data/', views.get_behavior_latest_day_data),
    #购买和收藏的转化率
    path('get_latest_conversion/', views.get_latest_conversion),
    #行为路径分析
    path('behaviorPath/',views.behaviorPath),
    path('rfm/', views.get_rfm_data),
    path('api/',views.getData)

]
