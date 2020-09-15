from store import views
from django.conf.urls import url

app_name = 'store'

urlpatterns = [
    url(r'^(?P<pk>\d+)/(?P<storename>[a-z]/products+$)', views.StoresView.as_view(), name='products'),
    url(r'^$',views.StoreView.as_view(), name='home'),
]
