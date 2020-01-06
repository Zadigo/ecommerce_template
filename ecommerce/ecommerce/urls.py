from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from ecommerce.views import HeroView

urlpatterns = [
    url(r'^$', HeroView.as_view(), name='hero'),
    path('admin/', admin.site.urls),
]
