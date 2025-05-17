from apps.orders import *
from django.urls import path

from apps.orders.views import *

urlpatterns=[
    path('orders/settlement/',OrderSettlementView.as_view()),
    path('orders/commit/',OrderCommitView.as_view())
]