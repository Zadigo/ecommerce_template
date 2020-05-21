from django.conf.urls import url
from dashboard import views

urlpatterns = [
    url(r'^settings/$', views.Settings.as_view(), name='settings'),
    url(r'^products/(?P<pk>\d+)/update$', views.UpdateProductView.as_view(), name='update'),
    url(r'^products/(?P<pk>\d+)/orders$', views.SingleProductOrdersView.as_view(), name='product_orders'),
    url(r'^products/(?P<method>(products|carts))/(?P<pk>\d+)/delete$', views.deleteview, name='delete_item'),
    url(r'^products/(?P<pk>\d+)/delete$', views.deleteview, name='delete_product'),
    url(r'^products/(?P<pk>\d+)$', views.ProductView.as_view(), name='dashboard_product'),
    url(r'^orders$', views.ProductOrdersView.as_view(), name='customer_orders'),
    url(r'^products/new$', views.CreateProductView.as_view(), name='dashboard_create'),
    url(r'^users/$', views.UsersView.as_view(), name='dashboard_users'),
    url(r'^carts/$', views.CartsView.as_view(), name='dashboard_carts'),
    url(r'^images/$', views.ImagesView.as_view(), name='manage_images'),
    url(r'^search/$', views.SearchView.as_view(), name='dashboard_search'),
    url(r'^products/$', views.ProductsView.as_view(), name='dashboard_products'),
    url(r'^$', views.IndexView.as_view(), name='index')
]