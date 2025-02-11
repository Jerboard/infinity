from django.urls import path
from . import views

urlpatterns = [
    path('order-status/', views.close_order_api, name='close_order_api'),
]
