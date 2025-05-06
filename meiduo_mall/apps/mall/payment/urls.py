from django.urls import path

from apps.mall.payment.views import *
urlpatterns=[

    path('payment/status/', PaymentStatusView.as_view()),
    path('payment/<order_id>/',PayUrlView.as_view()),
]