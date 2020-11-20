from django.conf.urls import url
from lookbook import views

app_name = 'lookbook'

urlpatterns = [
    url(r'^lookbook$', views.LookBookView.as_view(), name='lookbook'),
]
