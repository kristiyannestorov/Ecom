from django.contrib import admin
from django.urls import path, include
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('cart/', include('cart.urls')),
    path('payment/', include('payment.urls')),
]

# Serve media files even in production (not recommended long-term, but works for now)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)