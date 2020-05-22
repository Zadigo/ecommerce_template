from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ecommerce.views import HeroView

urlpatterns = [
    path('dashboard/', include('dashboard.urls')),
    path('shop/', include('shop.urls'), name='shop'),

    url(r'^$', HeroView.as_view(), name='home'),

    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
