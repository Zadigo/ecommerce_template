from django.conf.urls import url
from django.urls import include, path

from shop import views

cartpatterns = [
    url(r'^success$', views.CartSuccessView.as_view(), name='success'),
    url(r'^payment/process$', views.ProcessPayment.as_view(), name='payment_process'),
    url(r'^payment$', views.PaymentView.as_view(), name='payment'),
    url(r'^shipment$', views.ShipmentView.as_view(), name='shipment'),
    url(r'^alter/(?P<pk>\d+)/(?P<method>(add|reduce))$', views.alter_item_quantity, name='alter_quantity'),
    url(r'^(?P<pk>\d+)/delete$', views.delete_product_from_cart, name='delete_from_cart'),
    url(r'^coupon-add$', views.apply_coupon, name='add_coupon'),
    url(r'^no-cart$', views.EmptyCartView.as_view(), name='no_cart'),
    url(r'^$', views.CheckoutView.as_view(), name='checkout'),
]

urlpatterns = [
    path('cart/', include(cartpatterns)),

    url(r'^lookbook$', views.LookBookView.as_view(), name='lookbook'),
    url(r'^search$', views.SearchView.as_view(), name='search'),

    url(r'^private/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.PrivateProductView.as_view(), name='private'),
    url(r'^preview/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.PreviewProductView.as_view(), name='preview'),
    url(r'^special-offer/(?P<pk>\d+)/(?P<product_reference>[a-z]+)/$', views.SpecialOfferView.as_view(), name='special_offer'),
    
    url(r'^collections/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)/(?P<pk>\d+)/(?P<slug>[a-z\-]+)$', views.ProductView.as_view(), name='product'),
    url(r'^collections/(?P<gender>(femme|homme))/(?P<collection>[a-z]+)$', views.ProductsView.as_view(), name='collection'),
    url(r'^collections/(?P<gender>(femme|homme))$', views.ShopGenderView.as_view(), name='shop_gender'),

    url(r'^$', views.IndexView.as_view(), name='shop')
]
