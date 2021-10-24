import os

from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    path(os.getenv("URL_PREFIX", "") + "admin/", admin.site.urls),
    path(os.getenv("URL_PREFIX", ""), include("main.urls")),
    path(os.getenv("URL_PREFIX", "") + "api/", include("api.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
