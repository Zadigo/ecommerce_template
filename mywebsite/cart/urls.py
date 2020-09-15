from django.conf.urls import url
from django.urls.conf import include, path

from cart import views

app_name = 'cart'


apipatterns = [

]

urlpatterns = [
    url(r'^add-to-cart$', views.add_to_cart, name='add'),
    url(r'^payment/process$', views.ProcessPaymentView.as_view(), name='pay'),
    url(r'^coupon-add$', views.apply_coupon, name='add_coupon'),
    url(r'^alter/(?P<pk>\d+)/(?P<method>(add|reduce))$', views.alter_item_quantity, name='alter_quantity'),
    url(r'^(?P<pk>\d+)/delete$', views.delete_product_from_cart, name='delete'),

    url(r'^shipment$', views.ShipmentView.as_view(), name='shipment'),
    url(r'^payment$', views.PaymentView.as_view(), name='payment'),
    url(r'^success$', views.CartSuccessView.as_view(), name='success'),
    url(r'^no-cart$', views.EmptyCartView.as_view(), name='no_cart'),
    url(r'^$', views.CheckoutView.as_view(), name='checkout'),
]
