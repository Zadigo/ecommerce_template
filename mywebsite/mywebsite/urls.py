from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path, re_path
from django.views.generic import TemplateView

from mywebsite import rss, sitemaps, views

customer_cart_patterns = [
    # path('orders', TemplateView.as_view(template_name='others/faq/orders.html'), name='customer_care_orders'),
    # path('delivery', TemplateView.as_view(template_name='others/faq/delivery.html'), name='customer_care_delivery'),
    # path('returns', TemplateView.as_view(template_name='others/faq/returns.html'), name='customer_care_returns'),
    path('contact-us', TemplateView.as_view(template_name='others/faq/contact.html'), name='contact_us'),
    path('', views.CustomerServiceView.as_view(), name='customer_care'),

]

urlpatterns = [
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps.SITEMAPS}, name='django.contrib.sitemaps.views.sitemap'),

    path('customer-care/<page_name>/', views.CustomerServiceView.as_view(), name='customer_care_additional_pages'),
    path('customer-care/', include(customer_cart_patterns)),
    
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
