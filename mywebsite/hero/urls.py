from hero import views
from django.conf.urls import url

app_name = 'hero'

urlpatterns = [
    url(r'^$', views.HeroView.as_view(), name='home'),
]
