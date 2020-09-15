from django.conf.urls import url
from django.views.generic import TemplateView

from legal import views

app_name = 'legal'

urlpatterns = [
    url(r'^who-we-are$', TemplateView.as_view(template_name='pages/legal/who_are_we.html'), name='who_we_are'),
    url(r'^terms-of-service$', views.CGU.as_view(), name='use'),
    url(r'^terms-of-sale$', views.CGV.as_view(), name='sale'),
    url(r'^privacy$', views.Confidentialite.as_view(), name='privacy'),
]
