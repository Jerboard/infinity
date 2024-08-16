from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from admin_infinity import settings

urlpatterns = [
    path('admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += [path("ckeditor5/", include('django_ckeditor_5.urls')),]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
