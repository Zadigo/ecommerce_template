from django.conf.urls import include, url
from django.urls import path

from dashboard import views, api_views

app_name='dashboard'



apipatterns = [
    url(r'charts/(?P<name>[a-zA-Z]+)$', api_views.ChartsView.as_view(), name='chart')
]

collectionpatterns = [
    url(r'^(?P<pk>\d+)/update$', views.UpdateCollectionView.as_view(), name='update'),
    url(r'^new$', views.CreateCollectionView.as_view(), name='create'),
    url(r'^$', views.CollectionsView.as_view(), name='home'),
]

couponspatterns = [
    url(r'^(?P<pk>\d+)/activate$', views.activate_coupon, name='activate'),
    url(r'^(?P<pk>\d+)/update$', views.UpdateCouponsView.as_view(), name='update'),
    url(r'^new$', views.CreateCouponsView.as_view(), name='create'),
    url(r'^$', views.CouponsView.as_view(), name='home'),
]

imagespatterns = [
    url(r'^(?P<pk>\d+)/associate-image$', views.associate_images, name='associate'),

    url(r'^new', views.create_images, name='create'),
    url(r'^(?P<pk>\d+)$', views.ImageView.as_view(), name='update'),
    url(r'^$', views.ImagesView.as_view(), name='home'),
]

productpatterns = [
    url(r'^csv/upload$', views.upload_csv, name='upload_csv'),
    url(r'^csv/download$', views.download_csv, name='download_csv'),

    url(r'^(?P<pk>\d+)/unlink-image$', views.unlink_image_on_product_page, name='unlink'),
    url(r'^(?P<pk>\d+)/duplicate$', views.duplicate_view, name='duplicate'),
    url(r'^(?P<pk>\d+)/update$', views.UpdateProductView.as_view(), name='update'),
    url(r'^(?P<pk>\d+)/delete$', views.delete_product, name='delete'),


    url(r'^new$', views.CreateProductView.as_view(), name='create'),
    url(r'^$', views.ProductsView.as_view(), name='home'),
]

settingspatterns = [
    url(r'^analytics$', views.AnalyticsSettingsView.as_view(), name='analytics'),
    url(r'^store$', views.StoreSettingsView.as_view(), name='store'),
    url(r'^general$', views.GeneralSettingsView.as_view(), name='general'),

    url(r'^$', views.SettingsView.as_view(), name='home'),
]





urlpatterns = [
    path('api/', include((apipatterns, app_name), namespace='api')),
    path('collections/', include((collectionpatterns, app_name), namespace='collections')),
    path('coupons/', include((couponspatterns, app_name), namespace='coupons')),
    path('images/', include((imagespatterns, app_name), namespace='images')),
    path('products/', include((productpatterns, app_name), namespace='products')),
    path('settings/', include((settingspatterns, app_name), namespace='settings')),

    url(r'^(?P<method>(products|carts))/(?P<pk>\d+)/delete$', views.delete_item_via_table, name='delete_item'),
    
    url(r'^purchase/orders/new$', views.PurchaseOrderView.as_view(), name='create_purchase_order'),

    url(r'^tables-actions$', views.table_actions, name='table_actions'),

    url(r'^orders/(?P<pk>\d+)$', views.CustomerOrderView.as_view(), name='customer_order'),
    url(r'^orders$', views.CustomerOrdersView.as_view(), name='customer_orders'),

    url(r'^customers/new$', views.CreateCustomerView.as_view(), name='create_customer'),
    url(r'^users/(?P<pk>\d+)$', views.UserView.as_view(), name='dashboard_user'),
    url(r'^users/$', views.UsersView.as_view(), name='dashboard_users'),

    url(r'^carts/$', views.CartsView.as_view(), name='carts'),
    url(r'^search/$', views.SearchView.as_view(), name='search'),
    url(r'^$', views.IndexView.as_view(), name='index')
]
