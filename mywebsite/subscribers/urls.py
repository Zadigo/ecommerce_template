from subscribers import views
from django.conf.urls import url

app_name = 'subscribers'

urlpatterns = [
    url(r'^subscribe/', views.subscribe_by_email, name='email_subscription'),
]
