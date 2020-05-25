from django.conf.urls import url
from django.urls import include, path, re_path

from shop import views

urlpatterns = [
    url(r'^cart/success$', views.CartSuccessView.as_view(), name='success'),
    url(r'^cart/payment/process$', views.ProcessPayment.as_view(), name='payment_process'),
    url(r'^cart/payment$', views.PaymentView.as_view(), name='payment'),
    url(r'^cart/shipment$', views.ShipmentView.as_view(), name='shipment'),
    url(r'^cart/alter/(?P<pk>\d+)/(?P<method>(add|reduce))$', views.alter_item_quantity, name='alter_quantity'),
    url(r'^cart/(?P<pk>\d+)/delete$', views.delete_product_from_cart, name='delete_from_cart'),
    url(r'^cart/coupon-add$', views.apply_coupon, name='add_coupon'),
    url(r'^cart$', views.CheckoutView.as_view(), name='checkout'),
    url(r'^no-cart/$', views.EmptyCartView.as_view(), name='no_cart'),

    url(r'^products/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.ProductView.as_view(), name='product'),
    url(r'^products/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)$', views.ProductsView.as_view(), name='collection'),
    url(r'(?P<gender>(femme|homme))$', views.ShopView.as_view(), name='shop_gender'),
    url(r'^$', views.IndexView.as_view(), name='shop')
]
