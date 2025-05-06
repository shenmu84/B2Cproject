from django.urls import path
from views import *

urlpatterns = [
    path('admin/login/', UmsAdminLoginView.as_view()),
    # 更多的路由...
]
