import debug_toolbar
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from mywebsite import rss, sitemaps, views

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps.SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),
    
    url(r'^oauth/', include('social_django.urls', namespace='social')),

    path('customer-care/', include('customercare.urls')),
    path('subscribers/', include('subscribers.urls')),
    path('legal/', include('legal.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('shop/', include('shop.urls')),
    path('', include('hero.urls')),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error pages
handler404 = 'mywebsite.views.handler404'
handler500 = 'mywebsite.views.handler500'
