from django.conf.urls import url
from django.urls.conf import include, path, re_path
from django.views.generic import TemplateView

from customercare import views

app_name = 'customer_care'

customer_cart_patterns = [
    # path('orders', TemplateView.as_view(template_name='others/faq/orders.html'), name='customer_care_orders'),
    # path('delivery', TemplateView.as_view(template_name='others/faq/delivery.html'), name='customer_care_delivery'),
    # path('returns', TemplateView.as_view(template_name='others/faq/returns.html'), name='customer_care_returns'),
    path('contact-us', TemplateView.as_view(template_name='others/faq/contact.html'), name='contact_us'),
    path('', views.CustomerServiceView.as_view(), name='customer_care'),
]

urlpatterns = [
    path('customer-care/<page_name>/', views.CustomerServiceView.as_view(), name='customer_care_additional_pages'),
    # path('customer-care/', include(customer_cart_patterns)),
    url(r'^$', views.CustomerServiceView.as_view(), name='home')
]
