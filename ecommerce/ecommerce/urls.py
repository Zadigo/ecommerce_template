from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from ecommerce.views import HeroView

urlpatterns = [
    url(r'^$', HeroView.as_view(), name='home'),
    path('shop/', include('shop.urls'), name='shop'),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
