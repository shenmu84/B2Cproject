from apps.orders import *
from django.urls import path

from apps.orders.views import OrderSettlementView

urlpatterns=[
    path('order/settlement/',OrderSettlementView.as_view())
]