"""
URL configuration for meiduo_mall project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

from utils.converters import UsernameConverter
from django.urls import register_converter

register_converter(UsernameConverter, 'username')

# API版本控制
API_V1_PREFIX = 'api/v1/'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API URLs
    path(API_V1_PREFIX, include([
        path('users/', include('apps.mall.users.urls', namespace='users')),
        path('verifications/', include('apps.mall.verifications.urls', namespace='verifications')),
        path('areas/', include('apps.mall.areas.urls', namespace='areas')),
        path('oauth/', include('apps.mall.oauth.urls', namespace='oauth')),
        path('goods/', include('apps.mall.goods.urls', namespace='goods')),
        path('carts/', include('apps.mall.carts.urls', namespace='carts')),
        path('orders/', include('apps.mall.orders.urls', namespace='orders')),
        path('payment/', include('apps.mall.payment.urls', namespace='payment')),
        path('search/', include('apps.mall.search.urls', namespace='search')),
        path('contents/', include('apps.mall.contents.urls', namespace='contents')),
    ])),
    
    # Frontend URLs - 使用never_cache装饰器防止缓存
    path('', never_cache(TemplateView.as_view(template_name='index.html')), name='index'),
    path('login/', never_cache(TemplateView.as_view(template_name='login.html')), name='login'),
    path('register/', never_cache(TemplateView.as_view(template_name='register.html')), name='register'),
    path('cart/', never_cache(TemplateView.as_view(template_name='cart.html')), name='cart'),
    path('search/', never_cache(TemplateView.as_view(template_name='search.html')), name='search'),
    path('list/', never_cache(TemplateView.as_view(template_name='list.html')), name='list'),
    path('detail/<int:sku_id>/', never_cache(TemplateView.as_view(template_name='detail.html')), name='detail'),
    path('user/center/', never_cache(TemplateView.as_view(template_name='user_center_info.html')), name='user_center'),
    path('user/order/', never_cache(TemplateView.as_view(template_name='user_center_order.html')), name='user_order'),
    path('user/pass/', never_cache(TemplateView.as_view(template_name='user_center_pass.html')), name='user_pass'),
    path('user/site/', never_cache(TemplateView.as_view(template_name='user_center_site.html')), name='user_site'),
    path('place_order/', never_cache(TemplateView.as_view(template_name='place_order.html')), name='place_order'),
    path('order_success/', never_cache(TemplateView.as_view(template_name='order_success.html')), name='order_success'),
    path('pay_success/', never_cache(TemplateView.as_view(template_name='pay_success.html')), name='pay_success'),
    path('oauth_callback/', never_cache(TemplateView.as_view(template_name='oauth_callback.html')), name='oauth_callback'),
    path('success_verify_email/', never_cache(TemplateView.as_view(template_name='success_verify_email.html')), name='success_verify_email'),
    path('goods_judge/', never_cache(TemplateView.as_view(template_name='goods_judge.html')), name='goods_judge'),
]

# 开发环境静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # 生产环境静态文件服务
    urlpatterns += [
        path('static/<path:path>', serve, {'document_root': settings.STATIC_ROOT}),
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
