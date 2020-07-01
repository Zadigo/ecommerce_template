from django.conf.urls import url
from dashboard import views

urlpatterns = [
    url(r'^settings/$', views.Settings.as_view(), name='settings'),

    url(r'^coupons/(?P<pk>\d+)/update$',
        views.UpdateCouponsView.as_view(), name='coupon_update'),
    url(r'^coupons/new$', views.CreateCouponsView.as_view(),
        name='dashboard_coupons_new'),
    url(r'^coupons$', views.CouponsView.as_view(), name='dashboard_coupons'),

    url(r'^purchase/orders/new$', views.PurchaseOrderView.as_view(),
        name='create_purchase_order'),

    url(r'^customers/new$', views.CreateCustomerView.as_view(),
        name='create_customer'),

    url(r'^collections/new$', views.CreateCollectionView.as_view(),
        name='create_collection'),
    url(r'^collections/(?P<pk>\d+)/update$',
        views.UpdateCollectionView.as_view(), name='update_collection'),
    url(r'^collections$', views.CollectionsView.as_view(),
        name='dashboard_collections'),

    url(r'^products/csv/upload$', views.upload_csv, name='upload_csv'),
    url(r'^products/csv$', views.download_csv, name='download_csv'),

    url(r'^products/(?P<pk>\d+)/duplicate$',
        views.duplicate_view, name='duplicate'),
    url(r'^products/(?P<pk>\d+)/update$',
        views.UpdateProductView.as_view(), name='update'),
    url(r'^products/new/preflight$', views.preflight_images,
        name='dashboard_preflight_create'),
    url(r'^products/new$', views.CreateProductView.as_view(), name='dashboard_create'),

    url(r'^products/(?P<pk>\d+)/orders$',
        views.ProductOrdersView.as_view(), name='product_orders'),

    url(r'^products/(?P<method>(products|carts))/(?P<pk>\d+)/delete$',
        views.delete_view, name='delete_item'),
    url(r'^products/(?P<pk>\d+)/delete$',
        views.delete_product_update_page, name='dashboard_delete_product'),
    url(r'^products/(?P<pk>\d+)$',
        views.ProductView.as_view(), name='dashboard_product'),

    url(r'^orders/(?P<pk>\d+)$',
        views.CustomerOrderView.as_view(), name='customer_order'),
    url(r'^orders$', views.CustomerOrdersView.as_view(), name='customer_orders'),

    url(r'^users/(?P<pk>\d+)$', views.UserView.as_view(), name='dashboard_user'),
    url(r'^users/$', views.UsersView.as_view(), name='dashboard_users'),

    url(r'^images/new', views.create_images, name='create_images'),
    url(r'^images/(?P<pk>\d+)$', views.ImageView.as_view(), name='manage_image'),
    url(r'^images/$', views.ImagesView.as_view(), name='manage_images'),

    url(r'^carts/$', views.CartsView.as_view(), name='dashboard_carts'),
    url(r'^search/$', views.SearchView.as_view(), name='dashboard_search'),
    url(r'^products/$', views.ProductsView.as_view(), name='dashboard_products'),
    url(r'^$', views.IndexView.as_view(), name='index')
]

urlpatterns += [
    url(r'^api/charts/(?P<name>[a-zA-Z]+)$',
        views.ChartsView.as_view(), name='charts_endpoint')
]
