from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from accounts import views
from accounts.views_profile import ProfileView, ProfileDeleteView, ProfileDataView, PaymentMethodsView, ChangePasswordView

urlpatterns = [
    url(r'^oauth/', include('social_django.urls', namespace='social')),
    
    url(r'^profile/payment-methods/$', PaymentMethodsView.as_view(), name='payment_methods'),
    url(r'^profile/delete/$', ProfileDeleteView.as_view(), name='delete_account'),
    url(r'^profile/data/$', ProfileDataView.as_view(), name='profile_data'),
    url(r'^profile/change-password/$', ChangePasswordView.as_view(), name='change_password'),
    
    url(r'^forgot-password/confirm/(?P<uidb64>[A-Z]+)/(?P<token>\d+\w?\-[a-z0-9]+)', 
            views.UnauthenticatedChangePasswordView.as_view(), name='password_reset_confirm'),
    url(r'^forgot-password/$', views.ForgotPasswordView.as_view(), name='forgot_password'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^signup/$', views.SignupView.as_view(), name='signup'),
    
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
]
