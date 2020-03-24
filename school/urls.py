from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('',include(("schoolapp.urls", "schoolapp"), namespace = "schoolapp")),
    path('accounts/', include(('accounts.urls', "accounts"), namespace = "accounts")),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)