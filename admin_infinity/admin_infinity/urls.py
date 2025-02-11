from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from admin_infinity import settings
from bot_manager import views

urlpatterns = [
    path('', views.home_page_redirect, name='home_page'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('new_orders', views.new_orders_view, name='new_orders'),
    path('closed_orders', views.old_orders_view, name='closed_orders'),
    path('pay_setting', views.wallets_and_pay_methods_view, name='pay_setting'),
    path('promo_setting', views.promo_view, name='promo_setting'),
    path('switch', views.switch_view, name='switch'),
    path('admin/', admin.site.urls),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('api/v1/', include('api_1.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
