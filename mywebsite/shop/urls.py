from django.conf.urls import url
from django.urls import include, path

from shop import views

app_name='shop'

urlpatterns = [
    url(r'^size-guide/calculate$', views.size_calculator, name='calculator'),
    url(r'^size-guide$', views.SizeGuideView.as_view(), name='size_guide'),
    url(r'^lookbook$', views.LookBookView.as_view(), name='lookbook'),
    url(r'^search$', views.SearchView.as_view(), name='search'),

    url(r'^private/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.PrivateProductView.as_view(), name='private'),
    url(r'^preview/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.PreviewProductView.as_view(), name='preview'),
    
    url(r'^collections/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.ProductView.as_view(), name='product'),
    url(r'^collections/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)$', views.ProductsView.as_view(), name='collection'),
    url(r'^collections/(?P<gender>(femme|homme))$', views.ShopGenderView.as_view(), name='gender'),

    url(r'^$', views.IndexView.as_view(), name='home')
]
