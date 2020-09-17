from discounts import views
from django.conf.urls import url

app_name = 'discounts'

urlpatterns = [
    url(r'^special-offer/(?P<pk>\d+)/(?P<product_reference>[a-z]+)/$', views.SpecialOfferView.as_view(), name='offer'),
]
