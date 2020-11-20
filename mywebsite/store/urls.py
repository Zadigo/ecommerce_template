from django.conf.urls import url

from store import views

app_name = 'store'

urlpatterns = [
    url(r'^(?P<pk>\d+)/(?P<product>\d+)/(?P<slug>[a-z\-]+)$', views.StoreProductDetailView.as_view(), name='product'),
    url(r'^(?P<pk>\d+)$', views.StoreView.as_view(), name='products'),
    url(r'^$',views.StoresView.as_view(), name='home'),
]
